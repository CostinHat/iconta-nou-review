# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/tenants`.

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

from core import afirmatii as _af
from core import common as _common
from core import cont_valid as _cv
from core import db, auth_api, tenant_provisioning, facturi_api, clienti_api, salariati_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, vector_fiscal_api, firma_profil_api as _fp, observare as _obs, documente_api
from core import articole_import_api, retete_import_api
from core import repo_banca
from core import repo_casa
from core import repo_contabilitate
from core import repo_declaratii
from core import repo_efactura
from core import repo_facturi
from core import repo_firma_profil
from core import repo_mijloace_fixe
from core import repo_portal
from core import repo_reevaluari
from core import repo_salariati
from core import repo_stocuri
from core import repo_tenants
from core import repo_utilizatori
from core import spv_rute as _spv_rute
from core import tenant_stergere
from core import tranzactie
from core.common import nomenclator_cerut
from core.mesaje import CUI_FIRMA_LIPSA, PERIOADA_INCHISA, FARA_DREPT_VALIDARE, FARA_ACCES_TENANT
from core.pdf_util import bani, data_ro
from core.unde import Unde as _Unde
import os
import psycopg2.extras as _E_audit
import psycopg2.extras as _E_sol
from core import erori as _erori
from core import uc_comun as _uc_comun
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core.mesaje import (EMAIL_INVALID, EMAIL_EXISTA,
                         CUI_FIRMA_LIPSA,
                         MESAJ_Z_FARA_CHEIE,
                              FARA_DREPT_VALIDARE)
from core import nucleu as _nucleu, articole_import_api, retete_import_api, rip_migrare_api
import psycopg2 as _psycopg2
from core.mesaje import (EMAIL_INVALID, EMAIL_EXISTA,
                         CUI_FIRMA_LIPSA,
                         MESAJ_Z_FARA_CHEIE,
                              FARA_DREPT_VALIDARE)
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core import cronometru as _crono
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core.mesaje import (EMAIL_INVALID, EMAIL_EXISTA,
                         CUI_FIRMA_LIPSA,
                         MESAJ_Z_FARA_CHEIE,
                              FARA_DREPT_VALIDARE)


def tenants(inactive, ctx):
    """[P7 · use-case] Corpul rutei `/tenants`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return {"tenants": auth_api.tenantii_userului(conn, ctx["uid"], doar_active=not inactive)}


def tenant_scoatere_previzualizare(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/scoatere`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return tenant_stergere.previzualizare(conn, tenant_id)


def tenant_nume_ales(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nume-ales`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return tenant_provisioning.alege_denumirea(conn, tenant_id, date.alege, ctx["uid"])
        except ValueError as e:
            raise _erori.CerereGresita(str(e))


def tenant_scoate(tenant_id, confirmare, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            r = tenant_stergere.sterge(conn, tenant_id, "scoatere_firma", ctx["uid"],
                                       confirmare=confirmare)
        except PermissionError as e:
            raise _erori.Conflict(str(e))
        except ValueError as e:
            raise _erori.CerereGresita(str(e))
    # DUPĂ commit: un `rmtree` nu se dă înapoi.
    r["fisiere_sterse"] = tenant_stergere.sterge_fisiere(r["schema"])
    return r


def tenant_detalii(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        # verific accesul (schema_tenant întoarce None dacă userul n-are acces)
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    return d


def client_acces_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/client-acces`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            return {"clienti": repo_utilizatori.conturi_client_ale_firmei(cur, tenant_id)}


def client_acces_revoca(tenant_id, user_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/client-acces/{user_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            repo_utilizatori.dezactiveaza_clientul_firmei(cur, user_id, tenant_id)
            _uc_comun._urma_portal(cur, tenant_id, "acces_retras",
                         "cabinetul a retras accesul utilizatorului #%s" % user_id, ctx["uid"])
    return {"ok": True}


def acces_portal_preview(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/acces-portal`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            row = repo_utilizatori.primul_client_al_firmei(cur, tenant_id)
            # [F-preview] identitatea tenantului previzualizat: nume_tenant + tenant_are_cabinet
            # (accounting_firm_id setat) -> exact ce foloseste portal.js/_eGratuit ca la login.
            tr = repo_tenants.nume_si_cabinet(cur, tenant_id)
    if not row:
        raise _erori.CerereGresita("Firma nu are încă un cont de client. Invită unul din 'Acces client', apoi poți previzualiza.")
    # token de client, marcat preview -> read-only middleware blocheaza orice mutatie
    token = auth_api.emite_token({"id": row["id"], "rol": "client", "accounting_firm_id": None, "preview": True})
    # user cu contextul de tenant: fara el, tab-ul de preview cade pe portalul gratuit (bug F197).
    return {"token": token, "user": {"rol": "client",
                                     "nume_tenant": tr["nume"] if tr else None,
                                     "tenant_are_cabinet": bool(tr and tr["accounting_firm_id"])}}


def tenant_actualizeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        # [R77] `ctx["uid"]` nu e decorativ: o redenumire care se departeaza de denumirea de la
        # ANAF se consemneaza ca alegere deliberata, iar o alegere fara autor nu e o alegere.
        #
        # [LOTUL 11, 04.09.2026] `try` NU e decorativ nici el. Toate portile puse aici pe 27.08 —
        # cifra de control a CUI-ului, unicitatea CUI-ului, unicitatea denumirii — refuza ridicand
        # `ValueError`, iar ruta nu-l prindea: fiecare refuz iesea **500 Internal Server Error**.
        # Masurat apasand: `PUT /tenants/4838 {"cui": "123"}` -> 500. Mesajele scrise cu grija
        # („CUI invalid: cifra de control nu corespunde") n-au ajuns niciodata la un contabil.
        # *O poarta al carei refuz arata ca o cadere invata pe cineva ca aplicatia e stricata, nu
        # ca datele sunt gresite.*
        try:
            r = tenant_provisioning.actualizeaza_tenant(conn, tenant_id, date.nume, date.cui,
                                                        user_id=ctx["uid"])
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    return r


def tenant_plan_conturi_lista(tenant_id, q, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/plan-conturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            if q:
                rows = repo_contabilitate.conturi_dupa_text(cur, f"%{q}%", f"%{q}%")
            else:
                rows = repo_contabilitate.toate_conturile(cur)
    return {"conturi": [{"simbol": r[0], "denumire": r[1], "tip": r[2]} for r in rows]}


def tenant_plan_conturi_adauga(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/plan-conturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    simbol = (date.simbol or "").strip()
    denumire = (date.denumire or "").strip()
    if not simbol or not denumire:
        raise _erori.DateInvalide("Completează atât simbolul, cât și denumirea contului.")
    # [lotul 3, 04.09.2026] `simbol="ABC"` intra in plan si de acolo putea ajunge pe o nota, intr-o
    # balanta si intr-o declaratie. Criteriul e DERIVAT din nomenclatorul propriu: planul general
    # seed-uit la crearea firmei are peste 700 de conturi, toate incepand cu o cifra de clasa.
    if not simbol[0].isdigit() or simbol[0] == "0":
        raise _erori.DateInvalide("Simbolul contului începe cu cifra clasei (1-9), ca toate "
                                     "conturile din planul general — am primit %r. Dacă e un analitic, "
                                     "scrie-l după contul sintetic (de exemplu 4111.01)." % simbol)
    if not all(c.isdigit() or c in "._-/" for c in simbol):
        raise _erori.DateInvalide("Simbolul contului se scrie din cifre, cu separator pentru "
                                     "analitic (`.`, `_`, `-`, `/`) — am primit %r." % simbol)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            # Regula 4 + 14.4: un simbol care exista deja NU se suprascrie tacut (ar redenumi un cont OMFP
            # standard, seed-uit la crearea firmei). Calea bulk (solduri_api) foloseste ON CONFLICT DO NOTHING;
            # calea manuala refuza explicit, cu denumirea contului existent, si trimite la cautarea de mai sus.
            existent = repo_contabilitate.denumirea_contului(cur, simbol)
            if existent:
                raise _erori.Conflict("Contul %s există deja în plan: „%s”. Caută-l în lista de mai sus; dacă ai nevoie "
                        "de un cont diferit, folosește alt simbol." % (simbol, existent[0]))
            repo_contabilitate.adauga_cont_in_plan(cur, simbol, denumire, date.tip or "Bifunctional")
        conn.commit()
    return {"ok": True, "simbol": simbol}


def solduri_rezumat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solduri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_api.rezumat(conn)


def solduri_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solduri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [{"cont": r.cont, "denumire": r.denumire, "debit": r.debit, "credit": r.credit}
               for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return solduri_api.importa(conn, randuri, date.data_referinta)
        except ValueError as e:  # balanta neechilibrata -> 422 cu mesaj explicativ
            raise _erori.DateInvalide(str(e))


def parteneri_rezumat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_parteneri_api.rezumat(conn)


def parteneri_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [{"cont": r.cont, "cui": r.cui, "denumire": r.denumire, "debit": r.debit, "credit": r.credit}
               for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return solduri_parteneri_api.importa(conn, randuri, date.data_referinta)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj explicativ
            raise _erori.DateInvalide(str(e))


def salariati_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return salariati_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def asociati_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/asociati-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return asociati_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def retete_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return retete_import_api.importa(conn, schema, date.retete)


def articole_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/articole-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return articole_import_api.importa(conn, schema, randuri, data_sold=date.data_sold)
        except (ValueError, KeyError) as e:    # [lotul 6] refuzul ajunge ca mesaj, nu ca 500
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))


def mijloace_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/mijloace-fixe-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return mijloace_fixe_import_api.importa(conn, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def istoric_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/istoric-declaratii-import`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn() as conn:
        try:
            return istoric_declaratii_import_api.importa(conn, tenant_id, randuri)
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def produse_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"produse": produse_api.lista(conn)}


def produse_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.creeaza(conn, date.denumire, um=date.um,
                                pret_unitar=date.pret_unitar, cota_tva=date.cota_tva,
                                categorie=date.categorie, confirmat=date.confirmat)
    if not r.get("ok"):
        raise _erori.CerereGresita(r.get("mesaj", "produs invalid"))
    return r


def produse_actualizeaza(tenant_id, produs_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse/{produs_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.actualizeaza(conn, produs_id, denumire=date.denumire,
                                     um=date.um, pret_unitar=date.pret_unitar,
                                     cota_tva=date.cota_tva, categorie=date.categorie,
                                     confirmat=date.confirmat)
    if not r.get("ok"):
        raise _erori.Inexistent("produs inexistent")
    return r


def produse_sterge(tenant_id, produs_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse/{produs_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.sterge(conn, produs_id)
    if not r.get("ok"):
        raise _erori.Inexistent("produs inexistent")
    return r


def facturi_numerotare_get(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/numerotare`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return facturi_api.numerotare(conn)


def facturi_numerotare_set(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/numerotare`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = facturi_api.seteaza_numerotare(conn, serie=date.serie, numar_start=date.numar_start)
    if not r.get("ok"):
        raise _erori.CerereGresita(r.get("mesaj", "eroare"))
    return r


def scadentar_get(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/scadentar`; docstringul ei a ramas in stratul HTTP."""
    from core import scadentar as _sc
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _sc.pull(conn, schema)


def scadentar_optin(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/scadentar/opt-in`; docstringul ei a ramas in stratul HTTP."""
    from core import scadentar as _sc
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _sc.seteaza_optin(conn, date.activ)
    if not r.get("ok"):
        raise _erori.DateInvalide(r.get("mesaj", "eroare"))
    return r


def scadentar_supapa(tenant_id, factura_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/notificare`; docstringul ei a ramas in stratul HTTP."""
    from core import scadentar as _sc
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            r = _sc.seteaza_supapa(conn, factura_id, stop=date.stop,
                                   amanata_pana=date.amanata_pana)
    except ValueError as e:   # [lot 2] data amanarii invalida: mesaj, nu 500
        raise _erori.DateInvalide(str(e))
    if not r.get("ok"):
        raise _erori.Inexistent("factură inexistentă")
    return r


def firma_profil_get(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.citeste_profil(conn)


def firma_profil_regim_tva(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/regim-tva`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [F180] CUI din public.tenants -> apel ANAF live FARA a tine conexiunea pe schema
    with db.get_conn() as cpub:
        with cpub.cursor() as cur:
            row = repo_tenants.cui_dupa_id(cur, tenant_id)
    anaf_val, avert, tva_inceput = _uc_comun._anaf_tva_check(row[0] if row else None, date.platitor_tva)
    with db.get_conn(schema) as conn:
        # [R46] `platitor_tva` decide daca firma datoreaza D300/D394 si pe ce perioade.
        try:
            _fp.cere_perioade_deschise(conn, "Regimul de TVA")
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            repo_firma_profil.seteaza_platitor_tva(cur, date.platitor_tva)
        if anaf_val is not None:                      # ANAF a raspuns -> reimprospateaza snapshot (+ data inceput TVA)
            _fp.seteaza_snapshot_tva(conn, anaf_val, tva_inceput)
        conn.commit()
    r = {"ok": True, "platitor_tva": date.platitor_tva}
    if avert:                                          # divergenta -> informeaza, nu blocheaza
        r["avertisment"] = avert
    return r


def firma_profil_date(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/date`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.citeste_date(conn)


def firma_profil_date_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/date`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _fp.salveaza_date(conn, date, tenant_id=tenant_id)
    if not r.get("ok"):
        raise _erori.DateInvalide(r.get("mesaj", "date invalide"))
    return r


def firma_profil_model(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/model`; docstringul ei a ramas in stratul HTTP."""
    import re as _re
    if date.culoare and not _re.fullmatch(r"#[0-9a-fA-F]{6}", date.culoare.strip()):
        raise _erori.DateInvalide("Culoarea se scrie ca un cod hexazecimal de șase cifre, cu diez "
                                     "(de exemplu #1d4ed8) — am primit %r. Ea ajunge pe factura "
                                     "tipărită." % date.culoare)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _fp.salveaza_model(conn, font=date.font, culoare=date.culoare, logo=date.logo)


def fr_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-recurente`; docstringul ei a ramas in stratul HTTP."""
    from core import facturi_recurente as _fr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        return {"sabloane": _fr.lista(conn, schema)}


def fr_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-recurente`; docstringul ei a ramas in stratul HTTP."""
    from core import facturi_recurente as _fr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.adauga(conn, schema, corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def fr_comuta(tenant_id, sid, activ, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-recurente/{sid}`; docstringul ei a ramas in stratul HTTP."""
    from core import facturi_recurente as _fr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.comuta(conn, schema, sid, activ)
    if r.get("eroare"):
        raise _erori.Inexistent(r["eroare"])
    return r


def fr_sterge(tenant_id, sid, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-recurente/{sid}`; docstringul ei a ramas in stratul HTTP."""
    from core import facturi_recurente as _fr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        r = _fr.sterge(conn, schema, sid)
    if r.get("eroare"):
        raise _erori.Inexistent(r["eroare"])
    return r


def facturi_storno(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/storno`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            r = facturi_api.storneaza(conn, factura_id)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    return r


def vector_citeste(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vector`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return vector_fiscal_api.citeste(conn)


def vector_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vector`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # nume+cui din public.tenants (pt cazul cand firma_profil e gol si trebuie creat)  # [p83_upsert]
    with db.get_conn() as cpub:
        with cpub.cursor() as cur:
            row = repo_tenants.nume_si_cui_spatiat(cur, tenant_id)
    t_nume = row[0] if row else None
    t_cui = row[1] if row else None
    # [F180] apel ANAF live pe CUI INAINTE de a deschide conexiunea pe schema
    anaf_val, avert, tva_inceput = _uc_comun._anaf_tva_check(t_cui, date.platitor_tva)
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
            raise _erori.CerereGresita({"mesaj": _mesaj, "erori_campuri": [{"camp": _camp, "mesaj": _mesaj}]})
        raise _erori.CerereGresita(_mesaj)
    if avert:                                          # divergenta -> informeaza, nu blocheaza
        rez["avertisment"] = avert
    # marcheaza stratul de migrare ca gata
    try:
        with db.get_conn() as c:
            migrare_api.seteaza_status(c, ctx["firm"], "vector_fiscal", "gata", "")
    except Exception:
        pass
    return rez


def facturi_lista(tenant_id, an, luna, directie, limit, offset, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return {"facturi": facturi_api.lista_facturi(conn, an, luna, directie,
                                                         limit=limit, offset=offset)}
    except ValueError as e:   # [lot 2] filtru invalid: mesaj, nu 500 si nu lista goala tacuta
        raise _erori.DateInvalide(str(e))


def factura_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    # [A9 art.297 alin.2] TVA la incasare la furnizor -> deducere amanata (D300) + tip AI (D394).
    # Statutul se INGHEATA din ANAF (RTVAI.statusTvaIncasare), best-effort, INAINTE de conexiune
    # (ca platitor_tva_freeze: nu tinem o conexiune din pool peste apelul ANAF de 20s). Doar pe
    # PRIMITE cu CUI; fallback = ce a bifat contabilul. Pe emise nu se aplica.
    from core import anaf_api as _anaf
    _fti = date.furnizor_tva_incasare
    if date.directie == "primita" and str(date.tert_cui or "").strip():
        _fti = _anaf.furnizor_incasare_freeze(date.tert_cui, fallback=bool(date.furnizor_tva_incasare))
    try:
        with db.get_conn(schema) as conn:
            r = facturi_api.creeaza_factura(
                conn, date.numar, date.data_emitere, date.directie, linii,
                client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, data_scadenta=date.data_scadenta,
                moneda=date.moneda, status=date.status,
                tert_tara=date.tert_tara, tip_operatiune=date.tip_operatiune,
                furnizor_tva_incasare=_fti)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    return r


def factura_detalii(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id:int}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
    if not f:
        raise _erori.Inexistent("factură inexistentă")
    return f


def factura_sterge(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return facturi_api.sterge_factura(conn, factura_id)
    except _cf.RefuzContare as e:
        raise _erori.Conflict(e.mesaj)


def clienti_lista(tenant_id, status, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"clienti": clienti_api.lista_clienti(conn, status)}


def client_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return clienti_api.creeaza_client(conn, **date.model_dump())
    except ValueError as e:
        raise _erori.DateInvalide(str(e))


def client_detalii(tenant_id, client_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti/{client_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        c = clienti_api.detalii_client(conn, client_id)
    if not c:
        raise _erori.Inexistent("client inexistent")
    return c


def client_actualizeaza(tenant_id, client_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti/{client_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [lotul 9] Un client INEXISTENT primea `200 {"ok": false}` — un refuz deghizat in raspuns,
        # fara motiv si fara cod. „N-am putut actualiza" si „clientul asta nu exista" nu sunt
        # acelasi lucru, iar primul nu spune nimic.
        with conn.cursor() as cur:
            if not repo_portal.clientul_exista(cur, client_id):
                raise _erori.Inexistent("client inexistent")
        return clienti_api.actualizeaza_client(conn, client_id, **date.model_dump())


def client_sterge(tenant_id, client_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti/{client_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = clienti_api.sterge_client(conn, client_id)
    if not r["ok"] and r.get("cod") == "ARE_FACTURI":
        raise _erori.Conflict(r["mesaj"])
    return r


def salariati_lista(tenant_id, activ, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"salariati": salariati_api.lista_salariati(conn, activ)}


def salariat_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return salariati_api.creeaza_salariat(conn, **date.model_dump())
    except ValueError as e:
        _ec = getattr(e, "erori_campuri", None)  # [G10] contract {detail, erori_campuri}
        raise _erori.DateInvalide({"mesaj": str(e), "erori_campuri": _ec} if _ec else str(e))


def salariat_detalii(tenant_id, salariat_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        s = salariati_api.detalii_salariat(conn, salariat_id)
    if not s:
        raise _erori.Inexistent("salariat inexistent")
    return s


def salariat_actualizeaza(tenant_id, salariat_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [R51] `None` inseamna doua lucruri diferite: „n-am trimis campul" si „goleste-l".
    # `exclude_unset` le separa — ce a trimis clientul EXPLICIT cu null e o golire ceruta.
    trimise = date.model_dump(exclude_unset=True)
    golite = [k for k, v in trimise.items() if v is None]
    try:
        with db.get_conn(schema) as conn:
            # [lotul 7, 04.09.2026] `PUT /salariati/999999` raspundea `200 {"ok": true}` — „am
            # actualizat" despre cineva care nu e in firma. A TREIA oara in campanie cand o ruta
            # despre un salariat nu verifica daca el exista (lotul 4: concediile, de doua ori).
            with conn.cursor() as cur:
                if not repo_salariati.salariatul_exista(cur, salariat_id):
                    raise _erori.Inexistent("salariat inexistent")
            return salariati_api.actualizeaza_salariat(conn, salariat_id,
                                                       _golite=golite, **date.model_dump())
    except ValueError as e:
        _ec = getattr(e, "erori_campuri", None)  # [G10] contract {detail, erori_campuri}
        raise _erori.DateInvalide({"mesaj": str(e), "erori_campuri": _ec} if _ec else str(e))


def salariat_beneficiu_lunar(tenant_id, salariat_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/beneficiu-lunar`; docstringul ei a ramas in stratul HTTP."""
    from core import beneficii_api as _ben
    an, luna = corp.get("an"), corp.get("luna")
    if not isinstance(an, int) or not isinstance(luna, int) or luna < 1 or luna > 12:
        raise _erori.CerereGresita("an/luna invalide")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _ben.seteaza(conn, schema, salariat_id, an, luna, corp.get("tip"), corp.get("valoare"),
                         eveniment=corp.get("eveniment", ""), nr_copii=corp.get("nr_copii", 1))
        if r is None:
            raise _erori.Inexistent("salariat inexistent")
        if r.get("eroare"):
            raise _erori.CerereGresita(r["eroare"])
        return r


def salariat_sterge(tenant_id, salariat_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = salariati_api.sterge_salariat(conn, salariat_id)
    if not r["ok"] and r.get("cod") == "ARE_CONCEDII":
        raise _erori.Conflict(r["mesaj"])
    return r


def cm_lista(tenant_id, salariat_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/concedii`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [lotul 4] `salariat_id=999999` intorcea `{"concedii": []}` — „salariatul asta n-are concedii"
    # arata identic cu „salariatul asta nu exista". Iar `GET /fluturas`, pe ACELASI id inexistent,
    # raspunde `404 salariat inexistent`: aplicatia stia deosebirea intr-un loc si n-o facea in
    # celalalt. `an=1900` intorcea la fel, gol.
    _uc_comun._cere_perioada(an=an)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            if not repo_salariati.salariatul_exista_2(cur, salariat_id):
                raise _erori.Inexistent("salariat inexistent")
        return {"concedii": salariati_api.lista_concedii(conn, salariat_id, an)}


def cm_salveaza(tenant_id, salariat_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/concedii`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            with conn.cursor() as cur:
                if not repo_salariati.salariatul_exista_3(cur, salariat_id):
                    raise _erori.Inexistent("salariat inexistent")
            return salariati_api.salveaza_concediu(conn, salariat_id, corp)
    except (ValueError, ZeroDivisionError) as e:
        raise _erori.DateInvalide(str(e))


def cm_sterge(tenant_id, salariat_id, cm_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/concedii/{cm_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return salariati_api.sterge_concediu(conn, salariat_id, cm_id)


def cabinet_urme_portal(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/urme-portal`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            urme = [dict(x) for x in repo_utilizatori.urme_portal_ale_firmei(cur, tenant_id)]
    return {"urme": urme, "nr": len(urme)}


def bonuri_de_verificat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/de-verificat`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            bonuri = [{"id": r[0], "comerciant": r[1], "cui": r[2],
                       "data": r[3].isoformat() if r[3] else None,
                       "total": float(r[4] or 0),
                       "tva": (round(sum(float(x.get("valoare") or 0) for x in r[13]), 2)
                               if r[13] else float(r[5] or 0) + float(r[6] or 0)),
                       "articole": r[7] or [], "status": r[8],
                       "nr_imagini": r[9] or 0, "tip": r[10] or "bon",
                       "numar_document": r[11], "mentiuni": r[12],
                       "primit_la": r[14].isoformat() if r[14] else None,
                       "orientare": r[15] or 0}
                      for r in repo_casa.bonuri_de_verificat(cur, schema)]  # bon_flux_e9_v1
    return {"bonuri": bonuri}


def bon_aproba(tenant_id, bon_id, b, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/{bon_id}/aproba`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:  # bon_flux_e1b_v1
            rt = repo_casa.tipul_bonului(cur, schema, bon_id)
            if not rt:
                raise _erori.Inexistent("bon inexistent")
            if (rt[0] or "bon") != "bon":
                raise _erori.CerereGresita("documentul e chitanță; folosește stingerea de factură, nu contarea pe cheltuială")
        _uc_comun._cere_luna_deschisa(conn, schema, b.data)   # [R42 (a)] nota poartă data bonului
        suma_linii = sum(l.valoare for l in b.linii)
        if abs(suma_linii - b.total) > 0.05:
            raise _erori.CerereGresita(f"suma articolelor ({suma_linii}) != total ({b.total})")
        # valorile articolelor sunt cu TVA inclus; scad TVA proportional
        factor = (b.total - b.tva) / b.total if b.total else 1
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_bon_validata(cur, schema, b.data, f"BON-{bon_id}", f"Bon {b.comerciant}")[0]
            for l in b.linii:
                repo_contabilitate.adauga_linie_credit_casa(cur, schema, iid, l.cont, round(l.valoare * factor, 2))
            if b.tva:
                repo_contabilitate.adauga_linie_tva_din_casa(cur, schema, iid, b.tva)
            repo_casa.aproba_bonul(cur, schema, b.comerciant, b.data, b.total, iid, bon_id)
    return {"ok": True, "nota_id": iid}


def salarii_contare_propunere(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salarii-contare/propunere`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import salarii_contare as _sc
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            p = _sc.propunere(conn, schema, an, luna)
        except ValueError as e:
            # D112 nu se poate genera (profil incomplet). Refuzul lui e scris pentru contabil;
            # fara asta ar ajunge la el ca 500 gol.
            raise _erori.DateInvalide(str(e))
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        r = repo_contabilitate.id_nota_dupa_numar(cur, p["document_ref"])
    p["deja_contata"] = bool(r)
    p["nota_id"] = r[0] if r else None
    return p


def tenant_amortizare(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/amortizare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 7] `luna=13` dadea `500`, pe o ruta care scrie EVIDENTA
    from datetime import date as _date
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        # [R42 (a)] Nota de amortizare se datează în ziua 28 a lunii cerute (mai jos).
        _uc_comun._cere_luna_deschisa(conn, schema, _date(an, luna, 1).replace(day=28))
        ref = _date(an, luna, 1)
        with conn.cursor() as cur:
            if repo_contabilitate.nota_de_amortizare(cur, schema, f"AMORT-{an}-{luna:02d}"):
                raise _erori.CerereGresita("Amortizarea lunii e deja generată.")
            mf = repo_mijloace_fixe.de_amortizat(cur, schema)
        from core import d406_active as _d406
        linii = []
        for mid, den, cont_am, val, rez, dnf, pif, cont_imob, met, reev in mf:
            if not pif or not dnf:
                continue
            mf_d = {"cod": den, "denumire": den, "cont_imobilizare": cont_imob,
                    "cont_amortizare": cont_am, "valoare": val, "rezidual": rez,
                    "dnf_luni": dnf, "data_pif": pif, "metoda": met, "reevaluari": reev}
            try:
                rata = _d406.amortizare_luna(mf_d, an, luna)   # metoda reala (CF art.28), nu liniar
            except ValueError as e:
                raise _erori.DateInvalide(f"Amortizarea nu se poate genera pentru {den}: {e}")
            if rata > 0:
                linii.append((cont_am or "2813", float(rata), den))
        if not linii:
            return {"ok": True, "mesaj": "nimic de amortizat", "linii": 0}
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_amortizare_validata(cur, schema, _date(an, luna, 1).replace(day=28), f"AMORT-{an}-{luna:02d}", f"Amortizare {luna:02d}/{an}")[0]
            for cont_am, rata, den in linii:
                repo_contabilitate.adauga_linie_cheltuiala_amortizare(cur, schema, iid, cont_am, rata)
    return {"ok": True, "nota_id": iid, "linii": len(linii), "total": round(sum(r for _, r, _ in linii), 2)}


def perioade_blocate_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            return {"blocate": [{"an": r[0], "luna": r[1]} for r in repo_contabilitate.perioade_blocate(cur, schema)]}


def perioada_blocheaza(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate`; docstringul ei a ramas in stratul HTTP."""
    from core import inchidere_luna as _il
    from core import migrare_inchideri as _ui
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            ciorne = _uc_comun._ciorne_in_perioada(cur, schema, an, luna)
            facturi_desch = _uc_comun._facturi_neincheiate_in_perioada(cur, schema, an, luna)
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
            raise _erori.DateInvalide(dict(
                    _af.afirmatie(
                        "neconformitate", "inchidere_perioada",
                        "Luna %02d/%04d nu se poate închide." % (luna, an),
                        unde="perioada %02d/%04d" % (luna, an),
                        regula="o perioadă se închide doar după ce tot ce s-a întâmplat în ea e "
                               "înregistrat și validat"),
                    cod="PERIOADA_NU_SE_POATE_INCHIDE",
                    motive=motive, ciorne=ciorne, facturi=facturi_desch, blocaj=bl))
        with conn.cursor() as cur:
            repo_contabilitate.blocheaza_perioada(cur, schema, an, luna, ctx["uid"])
        _ui.scrie(conn, schema, an, luna, "inchisa", ctx["uid"])
        conn.commit()
    return {"blocat": f"{luna:02d}/{an}"}


def perioada_deblocheaza(tenant_id, an, luna, motiv, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate`; docstringul ei a ramas in stratul HTTP."""
    from core import migrare_inchideri as _ui
    if not (motiv or "").strip():
        raise _erori.DateInvalide({
                "cod": "REDESCHIDERE_FARA_MOTIV",
                "mesaj": "Redeschiderea unei perioade închise se consemnează cu motiv.",
                "camp": "motiv",
                "temei": "OMFP 1802/2014 — o perioadă închisă se redeschide ca act, nu prin ștergere."})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            repo_contabilitate.deblocheaza_perioada(cur, schema, an, luna)
        _ui.scrie(conn, schema, an, luna, "redeschisa", ctx["uid"], motiv.strip())
        conn.commit()
    return {"deblocat": f"{luna:02d}/{an}"}


def perioade_istoric(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate/istoric`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 6] `luna=13` si `an=1900` dadeau `{"istoric": []}`
    _uc_comun._cere_perioada(an, luna)   # [lotul 6] `luna=13` si `an=1900` intorceau `{"istoric": []}`
    from core import migrare_inchideri as _ui
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"istoric": _ui.istoric(conn, schema, an, luna)}


def tenant_jurnal(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            # [14-1-1] `nr_curent` se numara de la 1 IANUARIE, nu de la inceputul lunii: norma cere
            # "numarul curent al operatiunilor inregistrate incepand de la 1 ianuarie ... pana la
            # sfarsitul exercitiului financiar". De aceea fereastra e pe AN, iar filtrul pe luna se
            # aplica DUPA numerotare - altfel fiecare luna ar reincepe de la 1.
            note, total = {}, 0.0
            for (iid, data, nr, desc, sursa, status, fid, dref, nrc,
                 f_tip, f_serie, f_nr, f_data,
                 deb, cre, suma, cc_id, cc_nume) in repo_contabilitate.jurnal_pe_an(cur, schema, f"{an}-01-01", f"{an}-{luna:02d}-01"):
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


def tenant_stat_plata(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import stat_plata_api as _sp
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
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
            _reges_ok = repo_salariati.firma_are_chei_reges(_rc, tenant_id) is not None
        return {"stat": stat, "reges_configurat": _reges_ok}


def tenant_stat_emis(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata/emis`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import stat_plata_emis as _spe
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        ex = _spe.citeste(conn, schema, an, luna)
        return {"exemplare": ex, "contradictii": _spe.verifica(conn, schema, an, luna)}


def tenant_stat_motiv(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata/motiv`; docstringul ei a ramas in stratul HTTP."""
    from core import stat_plata_emis as _spe
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    try:
        eid = int(corp["exemplar_id"])
    except (KeyError, TypeError, ValueError):
        raise _erori.DateInvalide("cererea nu spune care exemplar al statului se asumă")
    with db.get_conn(schema) as conn:
        try:
            _spe.motiveaza(conn, schema, eid, corp.get("motiv") or "", de_cine=str(ctx["uid"]))
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    return {"ok": True}


def tenant_plata_salarii_preview(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/plata-salarii-preview`; docstringul ei a ramas in stratul HTTP."""
    from core import plata_salarii as _ps
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        cur = conn.cursor()
        nf = (repo_tenants.nume_dupa_id_2(cur, tenant_id) or [""])[0]
    with db.get_conn(schema) as conn:  # genereaza_pain001 foloseste nume necalificate -> search_path pe tenant
        try:
            _xml, meta = _ps.genereaza_pain001(conn, schema, an, luna, nume_firma_fallback=nf)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    return meta


def d390_clasificare_stare(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d390-clasificare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import d390_clasificare_api as _cl
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _cl.stare(conn, schema, an, luna)


def d390_reclasificare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d390-clasificare/reclasificare`; docstringul ei a ramas in stratul HTTP."""
    from core import d390_clasificare_api as _cl
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _cl.salveaza_reclasificare(conn, schema, corp.get("an"), corp.get("luna"),
                                       corp.get("directie"), corp.get("tara"), corp.get("cod"), corp.get("tip"))
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def d390_manual_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d390-clasificare/manual`; docstringul ei a ramas in stratul HTTP."""
    from core import d390_clasificare_api as _cl
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _cl.manual_adauga(conn, schema, corp.get("an"), corp.get("luna"), corp.get("tip"),
                              corp.get("tara"), corp.get("cod"), corp.get("den"), corp.get("baza"))
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def d390_manual_sterge(tenant_id, mid, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d390-clasificare/manual/{mid}`; docstringul ei a ramas in stratul HTTP."""
    from core import d390_clasificare_api as _cl
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (b)] Înainte de generare linia manuală e pregătire — o poate scoate un asistent.
        # După, e parte din declarația care există deja, iar ștergerea o face să nu mai
        # corespundă datelor din care a ieșit.
        if _uc_comun._declaratie_generata(conn, tenant_id, "D390", an, luna):
            _uc_comun._cere_admin_firma(ctx, "declarația D390 pe %02d/%d e deja generată — o linie completată "
                                   "manual face parte din ea, iar scoaterea ei o face să nu mai "
                                   "corespundă datelor din care a ieșit" % (luna, an))
        return _cl.manual_sterge(conn, schema, an, luna, mid)


def d301_operatiuni_lista(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d301-operatiuni`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import d301_operatiuni_api as _op
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _op.lista(conn, schema, an, luna)


def d301_operatiuni_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d301-operatiuni`; docstringul ei a ramas in stratul HTTP."""
    from core import d301_operatiuni_api as _op
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _op.adauga(conn, schema, corp.get("an"), corp.get("luna"), corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def d301_operatiuni_sterge(tenant_id, op_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d301-operatiuni/{op_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import d301_operatiuni_api as _op
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _op.sterge(conn, schema, an, luna, op_id)


def d300_manual_lista(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d300-manual`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import d300_manual_api as _dm
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _dm.lista(conn, schema, an, luna)


def d300_manual_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d300-manual`; docstringul ei a ramas in stratul HTTP."""
    from core import d300_manual_api as _dm
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _dm.adauga(conn, schema, corp.get("an"), corp.get("luna"), corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [G10] contract {mesaj, erori_campuri}
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def d300_manual_sterge(tenant_id, rid, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d300-manual/{rid}`; docstringul ei a ramas in stratul HTTP."""
    from core import d300_manual_api as _dm
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (b)] Aceeași regulă ca la D390. Perioada nu vine din cerere, ci din rândul însuși —
        # altfel s-ar putea șterge un rând dintr-o lună generată trimițând altă lună.
        with conn.cursor() as _cur_per:
            _r = repo_declaratii.perioada_d300_manual(_cur_per, schema, rid)
        if _r and _uc_comun._declaratie_generata(conn, tenant_id, "D300", _r[0], _r[1]):
            _uc_comun._cere_admin_firma(ctx, "declarația D300 pe %02d/%d e deja generată — un rând completat "
                                   "manual face parte din ea, iar scoaterea lui o face să nu mai "
                                   "corespundă datelor din care a ieșit" % (_r[1], _r[0]))
        return _dm.sterge(conn, schema, rid)


def tenant_pontaj_get(tenant_id, salariat_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`; docstringul ei a ramas in stratul HTTP."""
    from core import pontaj as _p
    from core import perioada as _per
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        g = _p.grila(conn, schema, salariat_id, an, luna)
        if g is not None:
            g["perioada_confirmata"] = _per.e_confirmat(conn, schema, an, luna, "pontaj")  # [cap.23]
    if g is None:
        raise _erori.Inexistent("salariat inexistent")
    return g


def tenant_pontaj_set(tenant_id, salariat_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/pontaj`; docstringul ei a ramas in stratul HTTP."""
    from core import pontaj as _p
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _p.seteaza(conn, schema, salariat_id, date.zi, date.stare, tenant_id=tenant_id)
    if not r.get("ok"):
        raise _erori.DateInvalide(r.get("mesaj", "eroare"))
    return r


def tenant_facturi_perioada(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/perioada`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import inchidere_luna as _il
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return _il.stare(conn, schema, an, luna)


def tenant_facturi_perioada_confirma(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/perioada/confirma`; docstringul ei a ramas in stratul HTTP."""
    from core import inchidere_luna as _il
    # [lotul 6] `luna=13` cadea cu `500` la confirmare si raspundea `{"ok": true}` la
    # redeschidere — adica „am redeschis" despre o luna care nu exista.
    _uc_comun._cere_perioada(date.an, date.luna)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            st = _il.confirma(conn, schema, date.an, date.luna, ctx.get("uid"))
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    return {"ok": True, "perioada": st}


def tenant_facturi_perioada_redeschide(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/perioada/redeschide`; docstringul ei a ramas in stratul HTTP."""
    from core import inchidere_luna as _il
    # [lotul 6] `luna=13` cadea cu `500` la confirmare si raspundea `{"ok": true}` la
    # redeschidere — adica „am redeschis" despre o luna care nu exista.
    _uc_comun._cere_perioada(date.an, date.luna)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        st = _il.redeschide(conn, schema, date.an, date.luna)
    return {"ok": True, "perioada": st}


def tenant_pontaj_confirma(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/pontaj/confirma`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(date.an, date.luna)   # [lotul 7] `luna=13` dadea `500`
    from core import perioada as _per
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        _per.confirma(conn, schema, date.an, date.luna, "pontaj", ctx.get("uid"))
        st = _per.e_confirmat(conn, schema, date.an, date.luna, "pontaj")
    return {"ok": True, "perioada_confirmata": st}


def bon_facturi_candidate(tenant_id, bon_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/{bon_id}/facturi-candidate`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_casa.cui_si_total_bon(cur, schema, bon_id)
            if not r:
                raise _erori.Inexistent("document inexistent")
            cui = (r[0] or "").upper().replace("RO", "").strip()
            suma = float(r[1] or 0)
            fc = [{"id": x[0], "numar": ((x[2] or "") + str(x[1] or "")).strip(),
                   "data": x[3].isoformat() if x[3] else None,
                   "total": float(x[4] or 0), "furnizor": x[5], "cui": x[6],
                   "potrivire_cui": bool(cui) and (x[6] or "").upper().replace("RO", "").strip() == cui,
                   "potrivire_suma": abs(float(x[4] or 0) - suma) <= 0.05} for x in repo_facturi.candidate_pentru_bon(cur, schema, cui, suma)]
    return {"facturi": fc}


def chitanta_stinge(tenant_id, bon_id, c, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/{bon_id}/stinge`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_casa.tip_si_status_bon(cur, schema, bon_id)
            if not r:
                raise _erori.Inexistent("document inexistent")
            if (r[0] or "bon") != "chitanta":
                raise _erori.CerereGresita("documentul nu e chitanta")
            if r[1] != "de_verificat":
                raise _erori.CerereGresita("documentul nu e in asteptare")
        rez = casa_api.adauga(conn, schema, {"data": c.data, "categorie": "plata_furnizor",
                                             "suma": c.suma, "document": c.document or ("CHIT-%d" % bon_id),
                                             "partener": c.partener, "cui": c.cui})
        if rez.get("eroare"):
            raise _erori.CerereGresita(rez["eroare"])
        with conn.cursor() as cur:
            repo_casa.aproba_bonul_cu_documente(cur, schema, c.factura_id, rez["id"], rez["inregistrare_id"], c.partener or None, c.data, c.suma, bon_id)
            if c.factura_id:
                repo_facturi.marcheaza_primita_platita(cur, schema, c.factura_id)
    return {"ok": True, "operatiune_id": rez["id"], "nota_id": rez["inregistrare_id"],
            "avertismente": rez.get("avertismente") or []}


def chitanta_emite(tenant_id, c, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/chitante`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    if c.suma <= 0:
        raise _erori.CerereGresita("suma trebuie să fie > 0")
    client_nume = client_cui = reprezentand = None
    total_fact = None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if c.factura_id:
                r = repo_facturi.factura_pentru_chitanta(cur, schema, c.factura_id)
                if not r:
                    raise _erori.Inexistent("factură inexistentă")
                if r[5] != "emisa":
                    raise _erori.CerereGresita("chitanta se emite doar pentru facturi emise")
                client_nume, client_cui, total_fact = r[2], r[3], float(r[4] or 0)
                nrtxt = str(r[1] or "")  # chitante_emise_v2_reprezentand: numar contine adesea si seria (ex. MD-2)
                if r[0] and not nrtxt.startswith(str(r[0])):
                    nrtxt = str(r[0]) + nrtxt
                reprezentand = "contravaloare factura %s din %s" % (
                    nrtxt, data_ro(r[6]))
            rs = repo_firma_profil.seria_chitantei(cur, schema)
            serie = (rs[0] if rs else None) or "CH"
            nr = repo_casa.urmatorul_numar_chitanta(cur, schema, serie)[0]
        rez = casa_api.adauga(conn, schema, {"data": c.data, "categorie": "incasare_client",
                                             "suma": c.suma, "document": "%s-%s" % (serie, nr),
                                             "partener": client_nume, "cui": client_cui})
        if rez.get("eroare"):
            raise _erori.CerereGresita(rez["eroare"])
        with conn.cursor() as cur:
            cid = repo_casa.adauga_chitanta(cur, schema, serie, nr, c.data, c.factura_id, client_nume, client_cui, c.suma, reprezentand, rez["id"], rez["inregistrare_id"])[0]
            if c.factura_id and total_fact is not None and c.suma >= total_fact - 0.005:
                repo_facturi.marcheaza_platita(cur, schema, c.factura_id)
    return {"ok": True, "chitanta_id": cid, "serie": serie, "numar": nr,
            "avertismente": rez.get("avertismente") or []}


def chitante_lista(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/chitante`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        if factura_id:
            _randuri = repo_casa.chitante_ale_facturii(cur, schema, factura_id)
        else:
            _randuri = repo_casa.chitante_toate(cur, schema)
        chi = [{"id": r[0], "serie": r[1], "numar": r[2], "data": r[3].isoformat() if r[3] else None,
                "suma": float(r[4] or 0), "client_nume": r[5]} for r in _randuri]
    return {"chitante": chi}


def cabinet_balanta_date(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/balanta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:  # balanta foloseste nume necalificate -> search_path pe tenant
        randuri = documente_api.balanta(conn, schema, an, luna)
    return {"randuri": randuri,
            "totaluri": documente_api.totaluri_balanta(randuri),
            "inchidere": documente_api.inchidere_balanta(randuri)}


def registru_fiscal_citeste(tenant_id, an, varianta, totalizare, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-evidenta-fiscala`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import registru_evidenta_fiscala as _ref
    if varianta not in _ref.VARIANTE:
        raise _erori.Inexistent("variantă necunoscută: %r" % varianta)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        if varianta == "venituri_pf":
            return _ref.registru_pf(conn, schema, an)
        try:
            return _ref.registru_profit(conn, schema, an, totalizare)
        except _ref.RegistruNeconstruibil:
            # 409, nu 400: cererea e legitimă, iar refuzul nu e al ei — e al nostru, și poartă de ce.
            # Corpul e o AFIRMAȚIE tipată, nu un dicționar de proză (decizia din 21.08): e o
            # afirmație despre datele firmei, iar `verificare_rupta` o ține să nu fie citită ca un
            # verdict gri permanent — „nu se poate pe trimestru", nu „nu există pe trimestru".
            raise _erori.Conflict(_ref.refuz_totalizare(an, totalizare))


def registru_fiscal_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-evidenta-fiscala`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_evidenta_fiscala as _ref
    an = corp.get("an")
    if not an:
        raise _erori.CerereGresita({
                "mesaj": "Nu am înscris rândul: lipsește anul.",
                "erori_campuri": [{"camp": "an", "mesaj": "cerut, nu poate lipsi"}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return _ref.adauga_pf(conn, schema, int(an), corp)
        except _ref.InregistrareIncompletaPF as e:
            raise _erori.CerereGresita({
                    "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                    "erori_campuri": [{"camp": e.camp, "mesaj": str(e)}],
                    "temei": e.temei})


def registru_inventar_citeste(tenant_id, exercitiu, momentul, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-inventar`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_inventar as _ri
    if momentul not in _ri.MOMENTE:
        raise _erori.Inexistent("moment necunoscut: %r" % momentul)
    # [lotul 3] `exercitiu=1900` intorcea un registru gol — cu temeiul legal citat langa el, ca si
    # cum ar fi fost un raspuns despre un exercitiu care exista.
    _uc_comun._cere_perioada(exercitiu=exercitiu)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _ri.registru(conn, schema, exercitiu, momentul)


def registru_inventar_propunere(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-inventar/propunere`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_inventar as _ri
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
    # [lotul 3] `luna=13` intorcea `{"an": 2026, "luna": 13, "randuri": []}` — adica repeta luna
    # imposibila inapoi, ca si cum ar fi o perioada goala.
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn(schema) as conn:  # balanta foloseste nume necalificate -> search_path pe tenant
        return {"an": an, "luna": luna, "randuri": _ri.solduri_de_pornire(conn, schema, an, luna)}


def registru_inventar_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-inventar`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_inventar as _ri
    exercitiu = corp.get("exercitiu")
    if not exercitiu:
        raise _erori.CerereGresita({
                "mesaj": "Nu am înscris rândul: lipsește exercițiul financiar.",
                "erori_campuri": [{"camp": "exercitiu", "mesaj": "cerut, nu poate lipsi"}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return _ri.adauga(conn, schema, int(exercitiu), corp)
        except _ri.InregistrareIncompleta as e:
            raise _erori.CerereGresita({
                    "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                    "erori_campuri": [{"camp": e.camp, "mesaj": _uc_comun._mesaj_scurt_inventar(e)}],
                    "temei": e.temei})


def registre_art321_citeste(tenant_id, fel, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registre-art321/{fel}`; docstringul ei a ramas in stratul HTTP."""
    from core import registre_art321 as _r
    if fel not in _r.FELURI:
        raise _erori.Inexistent("registru necunoscut: %r" % fel)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _r.registru(conn, schema, fel, an)


def registre_art321_adauga(tenant_id, fel, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registre-art321/{fel}`; docstringul ei a ramas in stratul HTTP."""
    from core import registre_art321 as _r
    if fel not in _r.FELURI:
        raise _erori.Inexistent("registru necunoscut: %r" % fel)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return _r.adauga(conn, schema, fel, corp)
        except _r.InregistrareIncompleta as e:
            # Mesajul de pe CAMP e scurt — el se randeaza langa un input, iar acolo un paragraf de
            # normа nu se citeste. Norma intreaga sta la nivelul refuzului, unde are loc.
            raise _erori.CerereGresita({
                    "mesaj": "Nu am înscris rândul: registrul cere un câmp pe care nu l-am primit.",
                    "erori_campuri": [{"camp": e.camp, "mesaj": "cerut de normă, nu poate lipsi"}],
                    "temei": e.temei})


def wc_config_get(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/woocommerce/config`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [wc_config_no_mask] o eroare de DB NU se ambaleaza intr-un 200 "neconfigurat" (masca cat.0) - se propaga
    # (500), iar frontend-ul arata eroare vizibila. "neconfigurat" ramane DOAR pentru lipsa reala de rand (r None).
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_firma_profil.config_woocommerce(cur, schema)
    if not r:
        return {"configurat": False, "url": None}
    return {"configurat": bool(r[0] and r[1]), "url": r[0]}


def wc_config(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/woocommerce/config`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [lotul 7, 04.09.2026] Un corp GOL scria `NULL` in toate trei cheile — adica **oprea canalul**,
    # tacut, si raspundea `{"ok": true}`. Chiar comentariul de deasupra o spune: „cu ele pline
    # canalul e pornit, golite il opreste". Aceeasi clasa ca importurile din lotul 1b: *o
    # operatiune de inlocuire care primeste un set vid nu are voie sa execute partea de stergere.*
    # Oprirea ramane posibila — dar ceruta, nu dedusa din tacere.
    # [R152, 05.09.2026] Gasit apasand: formularul umplut cu `«»@#$%` a fost ACCEPTAT, iar
    # ecranul a anuntat «Stare: conectat la «»@#$%». Doua neadevaruri intr-un rand — sirul nu
    # e o adresa, si nicio conexiune nu s-a incercat. Aici cade primul; al doilea, in
    # `woo_ecran.js`, care spune de acum ce stie: „configurat pentru”.
    _u = ((corp or {}).get("url") or "").strip()
    if _u:
        from urllib.parse import urlparse as _urlparse
        _p = _urlparse(_u)
        if _p.scheme not in ("http", "https") or "." not in (_p.netloc or ""):
            raise _erori.DateInvalide("Adresa magazinului nu e o adresă web: %r. Aștept ceva "
                                         "de forma https://magazin.ro." % _u)
    _campuri = [k for k in ("url", "ck", "cs") if k in (corp or {})]
    if not _campuri:
        raise _erori.DateInvalide("N-ai trimis niciun câmp. Cererea asta ar fi golit adresa "
                                     "magazinului și cheile lui, adică ar fi oprit canalul "
                                     "WooCommerce — dacă asta vrei, trimite explicit `url`, `ck` și "
                                     "`cs` goale.")
    with db.get_conn() as conn, conn.cursor() as cur:
        repo_firma_profil.seteaza_config_woocommerce(cur, schema, corp.get("url"), corp.get("ck"), corp.get("cs"))
        conn.commit()
    return {"ok": True}


def cabinet_solicitari_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solicitari`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_sol.RealDictCursor) as cur:
            rows = repo_portal.solicitarile_pentru_cabinet(cur, tenant_id)
    return {"solicitari": rows}


def cabinet_solicitari_raspunde(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solicitari`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    _de_trimis = None           # ce ramane de trimis DUPA ce se inchide blocul de conexiune
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            repo_portal.adauga_solicitare_2(cur, tenant_id, date.mesaj, ctx["uid"])
        conn.commit()
        email = _uc_comun._email_client_tenant(conn, tenant_id)
        if email:
            nume = _uc_comun._nume_tenant(conn, tenant_id)
            subiect = "Raspuns nou de la contabilul tau"
            html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                    "<p>Buna,</p><p>Contabilul tau ti-a raspuns la o solicitare pentru <b>" +
                    (nume or "firma ta") + "</b>:</p>"
                    "<p style='background:#f5f5f5;padding:14px;border-radius:8px'>" +
                    date.mesaj.replace("<", "&lt;").replace(">", "&gt;") + "</p>"
                    "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                    "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                    "Deschide portalul</a></p></div>")
            _de_trimis = (email, subiect, html)
    # [P5 val 3, 11.09.2026] AICI, nu inauntru. `conn.commit()` s-a facut mai sus, deci raspunsul e
    # deja in evidenta; apelul la Brevo (termen 15 s) nu mai tine nimic din pool. Se trimite exact
    # cand exista adresa clientului, ca inainte.
    if _de_trimis is not None:
        _obs.trimite_email_html(*_de_trimis)
    return {"ok": True}


def banca_rec_lista(tenant_id, status, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere`; docstringul ei a ramas in stratul HTTP."""
    _STARI_REC = ("noua", "potrivita", "contata", "ignorata")
    if status is not None and status not in _STARI_REC:
        raise _erori.DateInvalide("stare necunoscută: %r (stările reconcilierii: %s)"
                                     % (status, ", ".join(_STARI_REC)))
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"linii": _rec.lista(conn, schema, status)}


def banca_rec_conteaza(tenant_id, linie_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`; docstringul ei a ramas in stratul HTTP."""
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _rec.conteaza(conn, schema, linie_id, corp.get("alocari"))
    if rez is None:
        raise _erori.Inexistent("linie inexistentă")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def banca_rec_facturi(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/facturi-deschise`; docstringul ei a ramas in stratul HTTP."""
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"facturi": _rec.facturi_deschise_detalii(conn, schema)}


def rapoarte_comerciale(tenant_id, de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-comerciale`; docstringul ei a ramas in stratul HTTP."""
    if de and pana and str(pana) < str(de):
        raise _erori.DateInvalide("Sfârșitul intervalului (%s) e înaintea începutului (%s). "
                                     "Raportul se cere pe un interval, iar intervalul are o ordine."
                                     % (pana, de))
    from core import rapoarte_comerciale_api as _rc
    de, pana = _uc_comun._perioada_an(de, pana)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"vanzari": _rc.vanzari_pe_partener(conn, schema, de, pana),
                "durata_incasare": _rc.durata_medie_incasare(conn, schema, de, pana),
                "parteneri": _rc.lista_parteneri(conn, schema),
                "profit_produs": _rc.profit_pe_produs(conn, schema, de, pana),  # [punte_stoc_v1] F144 LIVE la CV
                "de": de, "pana": pana}


def rapoarte_comerciale_fisa(tenant_id, cui, de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-comerciale/fisa`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    de, pana = _uc_comun._perioada_an(de, pana)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _rc.fisa_partener(conn, schema, cui, de, pana)


def rapoarte_salvate_lista(tenant_id, tip_raport, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-salvate`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"variante": _rc.variante(conn, schema, tip_raport)}


def rapoarte_salvate_creeaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-salvate`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _rc.salveaza_varianta(conn, schema, corp.get("tip_raport", "comercial"),
                                    corp.get("nume"), corp.get("filtru"), ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"TIP_INVALID": "tip de raport necunoscut",
                  "NUME_GOL": "numele variantei e obligatoriu",
                  "NUME_EXISTA": "exista deja o varianta cu acest nume"}
        raise _erori.DateInvalide(mesaje.get(rez.get("cod"), "eroare"))
    return rez


def rapoarte_salvate_sterge(tenant_id, vid, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-salvate/{vid}`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _rc.sterge_varianta(conn, schema, vid)
    if not rez.get("ok"):
        raise _erori.Inexistent("variantă inexistentă")
    return rez


def registratura_lista(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registratura`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)   # [lotul 7] `an=1900` intorcea un registru gol, ca si cum ar exista
    from core import registratura_api as _reg
    import datetime as _dt
    an = an or _dt.date.today().year
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _reg.lista(conn, schema, an)


def registratura_creeaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registratura`; docstringul ei a ramas in stratul HTTP."""
    _d = (corp.get("data") or "").strip()
    if _d:
        from datetime import date as _date_reg
        try:
            _zi = _date_reg.fromisoformat(_d)
        except ValueError:
            raise _erori.DateInvalide("Data înregistrării nu e o dată: %r "
                                         "(aștept AAAA-LL-ZZ)." % _d)
        _uc_comun._cere_perioada(an=_zi.year)
    from core import registratura_api as _reg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _reg.inregistreaza(conn, schema, corp, ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"DIRECTIE_INVALIDA": "directie invalida (intrare/iesire)",
                  "DESCRIERE_GOALA": "descrierea e obligatorie"}
        raise _erori.DateInvalide(mesaje.get(rez.get("cod"), "eroare"))
    return rez


def contracte_sabloane_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"sabloane": _ct.lista_sabloane(conn, schema)}


def contracte_sabloane_salveaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _ct.salveaza_sablon(conn, schema, corp.get("id"), corp.get("nume"),
                                  corp.get("continut"), ctx["uid"])
    if not rez.get("ok"):
        mesaje = {"NUME_GOL": "numele sablonului e obligatoriu",
                  "CONTINUT_GOL": "continutul sablonului e obligatoriu",
                  "NUME_EXISTA": "Există deja un șablon cu numele ăsta. Alege alt nume, sau editează-l pe cel existent.",
                  "MARCAJ_INVALID": "marcaj necunoscut: {{%s}}" % rez.get("marcaj"),
                  "INEXISTENT": "sablon inexistent"}
        raise _erori.DateInvalide(mesaje.get(rez.get("cod"), "eroare"))
    return rez


def contracte_sabloane_sterge(tenant_id, sid, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane/{sid}`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _ct.sterge_sablon(conn, schema, sid)
    if not rez.get("ok"):
        raise _erori.Inexistent("sablon inexistent")
    return rez


def centre_cost_lista(tenant_id, doar_active, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost`; docstringul ei a ramas in stratul HTTP."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"centre": _cc.lista(conn, schema, doar_active=doar_active)}


def centre_cost_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost`; docstringul ei a ramas in stratul HTTP."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        r = _cc.adauga(conn, schema, corp.get("nume"))
        if r.get("eroare"):
            raise _erori.CerereGresita(r["eroare"])
        return r


def centre_cost_activ(tenant_id, centru_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/{centru_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        r = _cc.seteaza_activ(conn, schema, centru_id, bool(corp.get("activ", True)))
        if r is None:
            raise _erori.Inexistent("centru inexistent")
        return r


def centre_cost_raport(tenant_id, de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/raport`; docstringul ei a ramas in stratul HTTP."""
    if de and pana and str(pana) < str(de):
        raise _erori.DateInvalide("Sfârșitul intervalului (%s) e înaintea începutului (%s). "
                                     "Raportul se cere pe un interval, iar intervalul are o ordine."
                                     % (pana, de))
    """Realizat pe centru de cost, perioada [de, pana] (note validate, clasele 6/7)."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _cc.raport_realizat(conn, schema, de, pana)


def centre_cost_varianta(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/varianta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _cc.raport_varianta(conn, schema, an)


def centre_cost_buget(tenant_id, centru_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/{centru_id}/buget`; docstringul ei a ramas in stratul HTTP."""
    from core import centre_cost_api as _cc
    an = corp.get("an")
    if not isinstance(an, int) or an < 2020 or an > 2100:
        raise _erori.CerereGresita("an invalid")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        r = _cc.seteaza_buget(conn, schema, centru_id, an,
                              corp.get("buget_cheltuieli"), corp.get("buget_venituri"))
        if r is None:
            raise _erori.Inexistent("centru inexistent")
        if r.get("eroare"):
            raise _erori.CerereGresita(r["eroare"])
        return r


def banca_rec_ignora(tenant_id, linie_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/{linie_id}/ignora`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_banca.ignora_linia_de_extras(cur, schema, linie_id)
        conn.commit()
    if not r:
        raise _erori.CerereGresita("linie inexistentă sau deja contată")
    return {"ok": True}


def rip_lista(tenant_id, an, luna, status, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/registru`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.lista(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), an, luna, status)


def rip_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/operatiuni`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.adauga(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), corp, ctx["uid"])
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def rip_valideaza(tenant_id, op_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/operatiuni/{op_id}/valideaza`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.valideaza(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), op_id, ctx["uid"])
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def rip_sterge(tenant_id, op_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/operatiuni/{op_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.sterge(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), op_id)
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def rip_import_banca(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/import-banca`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.import_banca(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), an, luna, ctx["uid"])


def rip_import_casa(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/import-casa`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.import_casa(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), an, luna, ctx["uid"])


def rip_inventar(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/inventar/{an}`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        return _r.registru_inventar(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), an)


def rip_d212(tenant_id, an, optiune_cas, optiune_cass, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip/d212/{an}`; docstringul ei a ramas in stratul HTTP."""
    from core import rip_api as _r
    with db.get_conn() as conn:
        rez = _r.fisa_d212(conn, _uc_comun._rip_ctx(conn, ctx, tenant_id), an, optiune_cas, optiune_cass)
    if isinstance(rez, dict) and rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def concedii_coduri(tenant_id, la_data, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/concedii/coduri`; docstringul ei a ramas in stratul HTTP."""
    from core import coduri_cm_api as _cc
    import datetime as _d
    # [izolare] ruta e sub {tenant_id}, deci ACCESUL se verifica, chiar daca raspunsul nu depinde de
    # firma: altfel un 200 pe tenantul altui cabinet spune ca tenantul EXISTA. Prins de
    # test_izolare_structurala, nu de mine.
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent(FARA_ACCES_TENANT)
    d = None
    if la_data:
        try:
            d = _d.date.fromisoformat(la_data)
        except ValueError:
            raise _erori.DateInvalide("Data trebuie să fie în formatul AAAA-LL-ZZ.")
    return {"coduri": _cc.optiuni(d)}


def casa_registru(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/casa/registru`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _c.registru(conn, schema, an, luna)


def casa_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/casa/operatiuni`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _c.adauga(conn, schema, corp)
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def casa_sterge(tenant_id, op_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/casa/operatiuni/{op_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _c.sterge(conn, schema, op_id)
    if rez is None:
        raise _erori.Inexistent("operațiune inexistentă")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def stocuri_lista(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/nir`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 5] `luna=13` dadea `500`, `an=1900` dadea `200 {"nir": []}`
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"nir": _s.lista_nir(conn, schema, an, luna)}


def stocuri_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/nir`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _s.adauga_nir(conn, schema, corp)
    if rez.get("eroare"):
        _ec = rez.get("erori_campuri")  # [cap.24] contract {mesaj, erori_campuri} ca celelalte ecrane
        raise _erori.DateInvalide({"mesaj": rez["eroare"], "erori_campuri": _ec} if _ec else rez["eroare"])
    return rez


def stocuri_descarcare(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/descarcare`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _s.descarca_luna(conn, schema, an, luna)
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_articole(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"articole": _s.articole(conn, schema)}


def cv_fisa(tenant_id, articol_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _s.fisa(conn, schema, articol_id)
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    return rez


def cv_intrare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/intrare`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            rez = _s.intrare(conn, schema, corp)
        except (ValueError, KeyError) as e:   # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_iesire(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/iesire`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            rez = _s.iesire(conn, schema, corp)
        except (ValueError, KeyError) as e:   # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_inventar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/inventar`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return _s.inventar(conn, schema, corp)
        except (ValueError, KeyError) as e:      # [lotul 6] refuzul ajunge ca mesaj, nu ca 500
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))


def cv_locatii(tenant_id, articol_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/locatii`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        # [lotul 7] Un articol care NU EXISTA intorcea `{"locatii": []}` — „articolul asta nu e
        # nicaieri" arata identic cu „articolul asta nu exista". Aceeasi clasa ca salariatul din
        # lotul 4 si contul din lotul 3.
        if articol_id is not None and schema:
            with db.get_conn(schema) as _c2, _c2.cursor() as _cur:
                if not repo_stocuri.articolul_exista(_cur, articol_id):
                    raise _erori.Inexistent("articol inexistent")
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return {"locatii": _s.stoc_pe_locatii(conn, schema, articol_id)}


def cv_transfer(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/transfer`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            rez = _s.transfer(conn, schema, corp)
        except (ValueError, KeyError) as e:   # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_reclasificare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/reclasificare`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            rez = _s.reclasificare(conn, schema, corp)
        except (ValueError, KeyError) as e:   # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_analitica(tenant_id, zile_inert, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/analitica`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _s.analitica(conn, schema, zile_inert)


def cv_nivel_minim(tenant_id, articol_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _s.set_nivel_minim(conn, schema, articol_id, corp.get("nivel_minim"))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_barcode_gaseste(tenant_id, cod, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/barcode/{cod}`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        a = _s.gaseste_barcode(conn, schema, cod)
    if a is None:
        raise _erori.Inexistent("niciun articol cu acest cod de bare")
    return a


def cv_barcode_set(tenant_id, articol_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole/{articol_id}/barcode`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        rez = _s.set_barcode(conn, schema, articol_id, corp.get("barcode"))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cabinet_categorie_marime(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/categorie-marime`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import categorie_marime as _cm
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
    with db.get_conn(schema) as conn:
        return _cm.categorie(conn, schema, an)


def s1005_xml(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1005-xml`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise _erori.DateInvalide(str(e))
    return {"xml": xml, "avertismente": av}


def s1005_valideaza(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1005-valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise _erori.DateInvalide(str(e))
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
        _versiune = _duk.versiune_validator("s1005")           # [P5 val 3] citire de fisier, INAINTE
        with db.get_conn() as _c:
            _art.pastreaza(_c, schema, "s1005", str(an), xml,
                           produs_de_id=int(ctx["uid"]),
                           produs_de=ctx.get("nume") or str(ctx["uid"]),
                           verdict=("valid" if ok else "erori"),
                           verdict_versiune=_versiune,
                           verdict_amprenta=_art.amprenta(xml))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("[R45] artefact s1005 nepastrat: %s", _e)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


def s1003_xml(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1003-xml`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise _erori.DateInvalide(str(e))
    return {"xml": xml, "avertismente": av}


def s1003_valideaza(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1003-valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64, subprocess, tempfile, os
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            raise _erori.DateInvalide(str(e))
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
        _versiune = _duk.versiune_validator("s1003")           # [P5 val 3] citire de fisier, INAINTE
        with db.get_conn() as _c:
            _art.pastreaza(_c, schema, "s1003", str(an), xml,
                           produs_de_id=int(ctx["uid"]),
                           produs_de=ctx.get("nume") or str(ctx["uid"]),
                           verdict=("valid" if ok else "erori"),
                           verdict_versiune=_versiune,
                           verdict_amprenta=_art.amprenta(xml))
    except Exception as _e:
        import logging
        logging.getLogger("iconta").warning("[R45] artefact s1003 nepastrat: %s", _e)
    return {"ok": ok, "erori": erori, "avertismente": av,
            "xml_b64": base64.b64encode(xml.encode()).decode()}


def retete_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _r.lista(conn, schema)


def retete_salveaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        r = _r.salveaza(conn, schema, corp)
    if r.get("eroare"):
        _ec = r.get("erori_campuri")  # [cap.24] contract {mesaj, erori_campuri} ca facturi-recurente/emitere
        raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": _ec} if _ec else r["eroare"])
    return r


def retete_sterge(tenant_id, reteta_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete/{reteta_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _r.sterge(conn, schema, reteta_id)


def retete_descarca(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete/descarca`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return _r.descarca(conn, schema, corp)
        except (ValueError, KeyError) as e:      # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))


def verificare_stocuri(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/verificare-stocuri`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import stocuri_cv as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            arts = [dict(r) for r in repo_stocuri.articole_cu_cont(cur, schema)]
            val_cv = {}
            for a in arts:
                fisa = _m.fisa_magazie([dict(r) for r in repo_stocuri.miscari_ale_articolului(cur, schema, a["id"])])
                if fisa:
                    u = fisa[-1]
                    v = Decimal(str(u["sold_cantitate"] or 0)) * Decimal(str(u["cmp"] or 0))
                    val_cv[a["cont_stoc"]] = val_cv.get(a["cont_stoc"], Decimal("0")) + v
            rez = []
            for cont, vcv in sorted(val_cv.items()):
                sold = Decimal(str(repo_contabilitate.sold_initial_pe_cont(cur, schema, cont)["si"]))
                r = repo_contabilitate.rulaj_pe_cont_stoc(cur, schema, cont, cont)
                sold += Decimal(str(r["d"])) - Decimal(str(r["c"]))
                dif = (sold - vcv).quantize(Decimal("0.01"))
                rez.append({"cont": cont, "sold_contabil": str(sold.quantize(Decimal("0.01"))),
                            "valoare_fise_cv": str(vcv.quantize(Decimal("0.01"))),
                            "diferenta": str(dif), "ok": abs(dif) <= Decimal("0.01")})
    return {"conturi": rez, "ok": all(x["ok"] for x in rez),
            "nota": "Diferentele pot veni din note ciorna nevalidate sau operatiuni in afara fiselor CV."}


def etransport_xml(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/etransport-xml`; docstringul ei a ramas in stratul HTTP."""
    import re
    from core import etransport as _e
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_firma_profil.cui_firma(cur, schema) or {}
    cui = re.sub(r"\D", "", r.get("cui") or "")
    if not cui:
        raise _erori.DateInvalide(CUI_FIRMA_LIPSA)
    lipsa = _e.campuri_required_lipsa(corp)
    if lipsa:
        raise _erori.DateInvalide({"cod": "CAMPURI_LIPSA",
                "mesaj": "Câmpuri obligatorii lipsă (schema eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
                "campuri": lipsa})
    try:
        xml = _e.xml_notificare(cui, corp)
    except KeyError as e:
        raise _erori.DateInvalide(f"câmp lipsă: {e}")
    return {"xml": xml,
            "nota": "XML v2 pt. incarcare manuala in SPV (e-Transport). UIT-ul vine de la ANAF dupa upload."}


def etransport_trimite(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/etransport/trimite`; docstringul ei a ramas in stratul HTTP."""
    import re as _re2
    from core import etransport as _egen, etransport_send as _es
    principal = _spv_rute.spv_principal(ctx)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r0 = repo_firma_profil.cui_firma_2(cur, schema)
    cui = _re2.sub(r"\D", "", (r0[0] if r0 else "") or "")
    if not cui:
        raise _erori.DateInvalide(CUI_FIRMA_LIPSA)
    lipsa = _egen.campuri_required_lipsa(corp)
    if lipsa:
        raise _erori.DateInvalide({"cod": "CAMPURI_LIPSA",
                "mesaj": "Câmpuri obligatorii lipsă (schema eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
                "campuri": lipsa})
    try:
        xml = _egen.xml_notificare(cui, corp)
    except KeyError as e:
        raise _erori.DateInvalide("câmp lipsă: %s" % e)
    data_transport = (corp.get("transport") or {}).get("data")
    if not data_transport:
        raise _erori.DateInvalide("data transport lipsă")
    intracom = str(corp.get("cod_tip_operatiune")) == "10"   # AIC = achizitie intracomunitara -> UIT 15 zile
    mediu = os.environ.get("ETRANSPORT_MEDIU", os.environ.get("EFACTURA_MEDIU", "prod"))
    return _es.trimite(schema, principal, cui, xml, data_transport, intracom=intracom,
                       mediu=mediu, ref=corp.get("ref"))


def etransport_trimiteri_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/etransport/trimiteri`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            rows = repo_declaratii.trimiteri_etransport(cur, schema)
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


def banca_rec_reactiveaza(tenant_id, linie_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/{linie_id}/reactiveaza`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_banca.readuce_linia_de_extras(cur, schema, linie_id)
        conn.commit()
    if not r:
        raise _erori.DateInvalide("linia nu e ignorata")
    return {"ok": True}


def factura_recunoaste(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/recunoaste`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_facturi.stare_pentru_recunoastere(cur, schema, factura_id)
        if not r:
            raise _erori.Inexistent("factură inexistentă")
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
            raise _erori.DateInvalide("factura nu e o ciornă de recunoaștere (stare `%s`): actul e "
                                         "pentru facturile EMISE aduse prin import" % stare)
        try:
            with _cf.cursor_dict(conn) as cur:
                rez = _cf.contabilizeaza(cur, schema, factura_id, automat=True)
                repo_facturi.marcheaza_emisa(cur, schema, factura_id)
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "LUNA_INCHISA":
                raise _erori.Blocat(PERIOADA_INCHISA)
            raise _erori.DateInvalide(e.mesaj)
        conn.commit()
    return {"stare": "recunoscuta", "factura_id": factura_id, "contare": rez}


def factura_contabilizeaza(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            with _cf.cursor_dict(conn) as cur:
                rez = _cf.contabilizeaza(cur, schema, factura_id, automat=False)
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "INEXISTENTA":
                raise _erori.Inexistent(e.mesaj)
            # Codul de stare se pastreaza pe fiecare clasa de refuz: luna inchisa raspundea `423`
            # inainte de rescriere si raspunde `423` si acum. O rescriere care schimba tacit codul
            # de raspuns ar rupe apelanti fara sa spuna.
            if e.cod == "LUNA_INCHISA":
                raise _erori.Blocat(PERIOADA_INCHISA)
            raise _erori.DateInvalide(e.mesaj)
        conn.commit()
    return rez


def vanzare_marja(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-marja`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import tva_marja as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.vanzare_marja(corp["pret_vanzare"], corp["pret_cumparare"], _common.cota_ceruta(corp))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], (corp.get("descriere") or "Vanzare regim marja (art. 312)")[:200])[0]
            linii = [("4111", "707", Decimal(str(corp["pret_cumparare"])))]
            if r["marja_neta"] > 0:
                linii.append(("4111", "707", r["marja_neta"]))
            if r["tva"] > 0:
                linii.append(("4111", "4427", r["tva"]))
            for d, c, s in linii:
                if s > 0:
                    repo_contabilitate.adauga_linie_2(cur, schema, iid, d, c, s)
        conn.commit()
    return dict(_af.afirmatie(
        "fapt", "vânzare în regim de marjă", r["nota"] or "marjă calculată conform art. 312",
        unde=_Unde("inregistrare", iid),
        temei_completitudine="prețul de vânzare și cel de cumpărare din nota creată "
                             "(Cod fiscal art. 312, regimul marjei)"),
        inregistrare_id=iid, marja_bruta=str(r["marja_bruta"]),
        tva=str(r["tva"]), marja_neta=str(r["marja_neta"]), avertisment=r["nota"])


def vanzare_marja_turism(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-marja-turism`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import tva_marja_turism as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], (corp.get("descriere") or f"Vanzare marja turism ({regim}, art. 311)")[:200])[0]
            for d, c, s in linii:
                if s > 0:
                    repo_contabilitate.adauga_linie_2(cur, schema, iid, d, c, s)
        conn.commit()
    rasp["inregistrare_id"] = iid
    return rasp


def vanzare_aur_investitii(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-aur-investitii`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import tva_aur as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
                # [G5 · P7] Constrangerea in mesaj, nu doar verdictul: cod de dinainte de val, intrat
                # in domeniul lui G5 odata cu mutarea corpului rutei din `main.py` in use-case.
                raise ValueError("Suma livrării trebuie să fie mai mare decât 0; "
                                 "primit: %s." % suma)
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        mentiune = "taxare inversa (art. 331 al. 2 lit. h)" if regim == "taxare_inversa" \
                   else "scutit (art. 313 al. 3)"
        descr = (corp.get("descriere") or "Livrare aur investitii") + " - " + mentiune \
                + " - client: " + corp["client_identificare"]
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            repo_contabilitate.adauga_linie_venit_marfa(cur, schema, iid, suma)
        conn.commit()
    return {"inregistrare_id": iid, "regim": regim, "suma": str(suma)}


def achizitie_agricultor(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-agricultor`; docstringul ei a ramas in stratul HTTP."""
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.achizitie_de_la_agricultor(corp["valoare"], corp["agricultor_in_registru"])
            # [R54] confruntarea cu planul firmei inlocuieste verificarea de PREZENTA:
            # `cere_cont` refuza si absenta, si contul care nu exista in plan, si spune CE
            # cont si UNDE se creeaza. Doua verificari suprapuse ar fi doua locuri.
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie agricultor regim special (art. 315^1)") \
                + ((" - " + corp["agricultor"]) if corp.get("agricultor") else "")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for d, c, s in [(cont, "401", r["pret"]), ("4426", "401", r["compensatie"])]:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    return {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"])}


def vanzare_agricultor(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-agricultor`; docstringul ei a ramas in stratul HTTP."""
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.compensatie(corp["pret"])
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Livrare produse agricole") \
                + " - regim special agricultori (art. 315^1), compensatie 8%"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for s in (r["pret"], r["compensatie"]):
                repo_contabilitate.adauga_linie_venit_servicii(cur, schema, iid, s)
        conn.commit()
    return {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"])}


def cabinet_fisa_cont(tenant_id, an, cont, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/fisa-cont`; docstringul ei a ramas in stratul HTTP."""
    from core import fisa_cont as _fc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
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
                raise _erori.DateInvalide(str(e))
    return {"an": an, "luna": luna, "formular": _fc.COD_FORMULAR,
            "conturi": conturi, "fisa": fisa}


def jurnal_marja(tenant_id, tip, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal-marja`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    marker = {"secondhand": "art. 312", "turism": "art. 311"}.get(tip)
    if not marker:
        raise _erori.DateInvalide("tip invalid (secondhand|turism)")
    if len(luna) != 7 or luna[4] != "-":
        raise _erori.DateInvalide("luna format YYYY-MM")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            rows = repo_contabilitate.linii_pentru_jurnal_marja(cur, schema, "%" + marker + "%", luna)
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


def calcul_cm_endpoint(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/calcul-cm`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import salarizare as _s
    from core import scadente as _scad
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
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
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e) if isinstance(e, KeyError) else
                                "Anul, luna, salariatul și zilele de concediu medical se așteaptă ca "
                                "numere întregi: %s" % e)
    _uc_comun._cere_perioada(an, luna)
    if zile_cm < 0:
        raise _erori.DateInvalide("Zilele de concediu medical nu pot fi negative (am primit %d). "
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
        raise _erori.DateInvalide("Nu pot calcula media: salariatul nu are nicio lună lucrată în cele "
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
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    r["luni_in_baza"] = nr_luni
    r["venituri_baza"] = str(venituri)
    r["zile_baza"] = int(zile)
    # [baza_cm 22.08.2026] PE CE s-a facut media - o cifra fara sursa nu se poate contesta. Cand se
    # amesteca luni emise cu luni recalculate, contabilul trebuie s-o vada, nu s-o deduca.
    r["baza_temei"] = _b["temei"]
    r["baza_luni_emise"] = _b["luni_emise"]
    r["baza_luni_recalculate"] = _b["luni_recalculate"]
    return r


def factura_trimite_spv(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/trimite-spv`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_send as _efs          # EDateIncomplete — motorul fiscal
    from core import efactura_trimitere as _eft     # [P7 · D2] orchestrarea trimiterii
    principal = _spv_rute.spv_principal(ctx)   # token owner (cabinet XOR gratuit); 403 daca niciunul
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    mediu = os.environ.get("EFACTURA_MEDIU", "prod")
    try:
        r = _eft.trimite(schema, factura_id, principal, mediu=mediu)
    except _efs.EDateIncomplete as e:
        raise _erori.DateInvalide(str(e))
    except NotImplementedError as e:
        raise _erori.DateInvalide("Tip de factură netratat încă în e-Factura: %s" % e)
    st = r.get("stare")
    if st == "fara_token":
        raise _erori.Conflict(r.get("mesaj", "Conectează ANAF (SPV) înainte de a trimite."))
    if st == "deja_trimisa":
        raise _erori.Conflict("Factura are deja o trimitere activa in SPV (%s)." % r.get("stare_existenta"))
    if st == "nevalidat":
        return {"stare": "nevalidat", "erori": r.get("validare_mesaje", [])}
    return {"stare": st, "index_incarcare": r.get("index_incarcare"),
            "execution_status": r.get("execution_status"),
            "erori": r.get("errors") or ([r.get("raspuns", "")] if st in ("nok", "eroare_upload") else []),
            "mesaj": r.get("raspuns")}


def facturi_trimiteri_spv(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/trimiteri-spv`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            rows = repo_efactura.ultima_trimitere_per_factura(cur, schema)
    return {str(r[0]): {"stare": r[1], "index_incarcare": r[2], "error_message": r[3]} for r in rows}


def facturi_primite_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        out = []
        with conn.cursor() as cur:
            rows = repo_efactura.primite_in_asteptare(cur, schema)
            for (pid, cife, cifb, status, xmlb, fid) in rows:
                pr = repo_efactura.contul_invatat_al_emitentului(cur, schema, cife)
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


def factura_primita_xml(tenant_id, primita_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite/{primita_id}/xml`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_efactura.xml_brut(cur, schema, primita_id)
    if not r:
        raise _erori.Inexistent("factură primită inexistentă")
    return {"xml": r[0] or ""}


def factura_primita_respinge(tenant_id, primita_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite/{primita_id}/respinge`; docstringul ei a ramas in stratul HTTP."""
    motiv = (corp.get("motiv") or "").strip()
    if not motiv:
        raise _erori.DateInvalide("motivul respingerii e obligatoriu")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_efactura.starea_primitei_blocata(cur, schema, primita_id)
            if not r:
                raise _erori.Inexistent("factură primită inexistentă")
            if r[0] == "validata":
                raise _erori.Conflict("factura a fost deja validată")
            repo_efactura.marcheaza_primita_respinsa(cur, schema, motiv, primita_id)
        conn.commit()
    return {"stare": "respinsa"}


def reges_config(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reges-config`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        if corp.get("mediu", "test") not in ("test", "prod"):
            raise _erori.DateInvalide(nomenclator_cerut("mediu", "test|prod"))
        # [lotul 7] Corpul gol cadea mai jos, pe `corp["username"]`, cu `KeyError` neprins.
        for _c, _et in (("username", "utilizatorul REGES"), ("parola", "parola REGES")):
            if not str(corp.get(_c) or "").strip():
                raise _erori.DateInvalide("Lipsește %s. Fără el, trimiterile către REGES nu se pot "
                                             "autentifica." % _et)
        with conn.cursor() as cur:
            repo_salariati.salveaza_cheile_reges(cur, tenant_id, corp["username"], corp["parola"], corp.get("mediu", "test"))
        conn.commit()
    return {"ok": True}


def achizitie_taxare_inversa(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-taxare-inversa`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from datetime import date as _date
    from core import anaf_api as _anaf
    from core import taxare_inversa as _ti
    # ── [P5 val 3, 11.09.2026] ANAF ÎNAINTE de conexiune ────────────────────────────────
    # Statutul TVA al furnizorului se îngheață pe factură și depinde doar de payload. Forma
    # dinainte îl cerea din interiorul tranzacției, deci ținea o conexiune din pool peste un apel
    # cu termen de 20 s. `platitor_tva_freeze` e best-effort: ANAF jos → fallback, nu excepție.
    furnizor_cui = str(corp.get("furnizor_cui") or "").strip().upper().replace(" ", "")
    _furn_pl = str(corp.get("furnizor_platitor_tva", True)).strip().lower() not in ("false", "nu", "0")
    _tert_pl = _anaf.platitor_tva_freeze(furnizor_cui, fallback=_furn_pl) if furnizor_cui else _furn_pl
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            rand = repo_firma_profil.platitor_tva(cur, schema)
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
            if not furnizor_cui:      # calculat înaintea blocului; validarea rămâne aici (422)
                raise ValueError("CUI furnizor obligatoriu (taxare inversa e intre platitori RO - furnizor cu CUI)")
            numar = str(corp.get("numar") or "").strip()
            if not numar:
                raise ValueError("numar factura furnizor obligatoriu")
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie") + " - " + mentiune
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor RO cu CUI, categorie_331 -> codPR, taxare_inversa=True)
            #    = sursa citita de D394 (op1 tip C + op11 codPR). Linie cota reala -> baza/tva reverse-charge.
            # `_tert_pl` s-a înghețat înaintea blocului — v. nota de la începutul rutei
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": descr[:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": cota}],
                                       tert_nume=furnizor_nume or None, tert_cui=furnizor_cui,
                                       categorie_331=categorie, taxare_inversa=True, status="importata",
                                       tert_platitor_tva=_tert_pl)
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge 4426=4427, NU cea standard
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            for d, c, s in [(cont, "401", val), ("4426", "4427", tva)]:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva),
            "mentiune": mentiune}


def achizitie_ic(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-ic`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        from core import facturi_api as _fa
        try:
            val = Decimal(str(corp["valoare"]))
            # [R148] Art. 291 alin. (8): pentru AIC cota e cea in vigoare la data EXIGIBILITATII,
            # nu la data facturii. Cele doua difera cand factura furnizorului vine tarziu — atunci
            # exigibilitatea a intervenit deja, in ziua 15 a lunii urmatoare faptului generator
            # (art. 284 alin. 2). Aplicatia calcula deja exact asta pentru D390 (`d390.py:491`) si
            # valida cota pe alta data: doua date pentru acelasi fapt.
            _data_exig = _common.exigibilitate_aic(corp["data"], corp.get("data_faptului_generator"))
            tva = _ic.tva_taxare_inversa(
                val, _common.cota_ceruta({**corp, "data": _data_exig.isoformat()}))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            cod_tva_furnizor = str(corp.get("cod_tva_furnizor") or "").strip().upper().replace(" ", "")
            if not cod_tva_furnizor:
                raise ValueError("cod TVA furnizor UE obligatoriu (fara el achizitia NU ajunge in D390)")
            # [etapa 2, lotul F, 15.09.2026] TARA furnizorului, derivata din chiar codul lui de TVA.
            # Fara ea factura se scria cu implicitul `tert_tara="RO"`, iar D300 ruteaza pe TARA
            # (`d300.py:247-249`), nu pe codul partenerului: achizitia intracomunitara nu ajungea
            # nici la rd.5/rd.18 (bunuri), nici la rd.7/rd.20 (servicii). Nota contabila purta
            # taxarea inversa, decontul nu declara nimic — doua evidente care spun lucruri diferite
            # despre acelasi fapt. Prefixul se desparte cu helperul care stie si lista UE si cazul
            # Greciei (`intracomunitar.desparte_cod_tva`), nu cu `cod[:2]` scris aici: un `RO` scris
            # de doua ori e inceputul unei divergente.
            tara_furnizor, _nr_tva = _ic.desparte_cod_tva(cod_tva_furnizor)
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        tip = "servicii IC primite (art. 278(2))" if corp.get("tip") == "servicii"               else "achizitie intracomunitara bunuri (art. 268)"
        descr = (corp.get("descriere") or "AIC") + f" - {tip}, taxare inversa 4426=4427"
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor UE) = sursa citita de D390. Factura UE fara TVA RON
            #    (taxare inversa la beneficiar) -> linie cota 0 -> total=val, tva=0 -> baza D390 = val.
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": descr[:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": 0}],
                                       tert_nume=furnizor_nume or None, tert_cui=cod_tva_furnizor,
                                       tert_tara=tara_furnizor,
                                       # [R186, 16.09.2026] AXA, INGHETATA pe document. `corp["tip"]`
                                       # e deja validat contra nomenclatorului mai sus (bunuri|servicii,
                                       # orice altceva = refuz), deci ce se scrie e ce a declarat omul.
                                       # Pana azi valoarea intra doar in textul descrierii, iar D300
                                       # rutata pe implicit: serviciile IC ajungeau la rd.5, nu la rd.7.
                                       axa_ic=corp.get("tip"),
                                       data_faptului_generator=data_fg, status="importata")
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge, NU cea standard
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            for d, c, s in [(cont, "401", val), ("4426", "4427", tva)]:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva)}


def achizitie_neinregistrat(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-neinregistrat`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import facturi_api as _fa
    from core import d394 as _d394
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
            if not furnizor_nume:
                raise ValueError("nume furnizor obligatoriu (persoana fizica - apare in denP si in avertisment)")
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                raise ValueError("Valoarea operațiunii trebuie să fie un număr mai mare "
                                 "decât zero.")
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")  # [R54]
            numar = str(corp.get("numar") or "").strip() or ("BORDEROU-" + str(corp["data"]))
            categorie = str(corp.get("categorie") or "").strip() or None
            if categorie and not _d394.codpr_N_din_categorie(categorie):
                raise ValueError("categorie N invalida (nomenclator lit.D CODPR_N): %s" % categorie)
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achizitie de la neinregistrat") + " - " + furnizor_nume
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)
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
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            repo_contabilitate.adauga_linie_furnizor(cur, schema, iid, cont, val)
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val),
            "categorie": categorie, "in_d394": bool(categorie)}


def import_extracomunitar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/import-extracomunitar`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            rand = repo_firma_profil.platitor_tva_2(cur, schema)
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
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
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for d, c, s in linii:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    return {"inregistrare_id": iid, "taxa_vamala": str(r["taxa_vamala"]),
            "baza_tva": str(r["baza_tva"]), "tva": str(r["tva"]), "mod_tva": r["mod_tva"]}


def export_extracomunitar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/export-extracomunitar`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            ok, ment = _ie.valideaza_export(corp.get("tara_client"),
                                            bool(corp.get("dovada_export")))
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                raise ValueError("Valoarea operațiunii trebuie să fie un număr mai mare "
                                 "decât zero.")
            # [R54] confruntarea cu planul firmei stă ÎN try: refuzul e un mesaj pentru om
            # (422), nu o defecțiune (500). Era după `except`, deci ar fi ieșit 500.
            cont_venit = _cv.cere_cont(conn, schema,
                                       _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "707"),
                                       "cont_venit")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Export") + f" ({corp['tara_client']}) - " + ment
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            repo_contabilitate.adauga_linie_client(cur, schema, iid, cont_venit, val)
        conn.commit()
    return {"inregistrare_id": iid, "mentiune": ment}


def nota_tva_incasare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-tva-incasare`; docstringul ei a ramas in stratul HTTP."""
    from core import cota_tva_incasare as _c295
    from core import tva_incasare as _ti
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        sens = corp.get("sens")
        if sens not in ("incasare", "plata"):
            raise _erori.DateInvalide("sens invalid (incasare/plata)")
        try:
            # [R149] Art. 291 alin. (5), citit la sursa: *„In cazul operatiunilor supuse
            # sistemului TVA la incasare, cota aplicabila este cea in vigoare la data la care
            # intervine FAPTUL GENERATOR, cu exceptia situatiilor in care este emisa o factura sau
            # este incasat un avans, inainte de data livrarii/prestarii, pentru care se aplica cota
            # in vigoare la data la care a fost emisa factura ori la data la care a fost incasat
            # avansul."*
            #
            # Deci **data incasarii nu e, in nicio ramura, data care decide cota** — desi ea e data
            # la care intervine EXIGIBILITATEA (art. 282 alin. 3). Aici exigibilitatea si cota se
            # despart, si exact asta numea decizia prin „sau exigibilitatea, unde difera".
            #
            # Pana azi ruta valida cota pe `corp["data"]` = data incasarii. Consecinta: o livrare din
            # era 19%, incasata azi, ar fi avut cota 19 REFUZATA ca „nu e in vigoare" — o cifra
            # corecta respinsa. Se cere data faptului generator, si pe ea se verifica.
            # [R151, 05.09.2026] Care data decide cota — cele doua ramuri ale art. 291 alin. (5)
            # — e o REGULA FISCALA, si sta in modulul ei, `core/cota_tva_incasare`, unde fiecare
            # refuz isi poarta temeiul ca date. Ruta doar o cheama: aici nu se decide nimic
            # despre norma, se transporta alegerea contabilului.
            _al = _c295.alegerea(corp)
            tva = _ti.tva_din_incasare(
                corp["suma_incasata"],
                _common.cota_ceruta({**corp, "data": _al.data_cotei}))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        debit, credit = ("4428", "4427") if sens == "incasare" else ("4426", "4428")
        # [R151] Descrierea implicita numeste RAMURA aleasa: peste sase luni, cine citeste nota
        # trebuie sa poata reconstitui de ce cota e aia si nu alta. Fraza vine de la regula
        # (`cota_tva_incasare.descrierea`), nu se compune aici. O descriere scrisa de om nu se
        # suprascrie — ea e a lui.
        desc = corp.get("descriere") or (
            "TVA la incasare - exigibilitate la "
            + ("incasare (art. 282)" if sens == "incasare" else "plata furnizor")
            + "; " + _c295.descrierea(_al))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], desc[:200])[0]
            repo_contabilitate.adauga_linie_5(cur, schema, iid, debit, credit, tva)
        conn.commit()
    return {"inregistrare_id": iid, "tva_exigibil": str(tva), "nota": f"{debit}={credit}"}


def reevaluare_valuta(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reevaluare-valuta`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import diferente_curs as _dc
    from core import curs_bnr as _cb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            data = _date.fromisoformat(corp["data"])
            solduri = corp["solduri"]
            if not solduri:
                raise ValueError("solduri gol")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        linii, detalii = [], []
        try:
            for s in solduri:
                try:
                    curs_bnr, _dcurs, _sursa = _cb.curs_pentru(conn, s.get("moneda", "EUR"), data)
                except _cb.MonedaNecotata as _mn:   # [lotul 8] aceeasi gaura, a doua cale
                    raise _erori.DateInvalide(str(_mn))
                except _cb.CursIndisponibil as _ci:
                    raise _erori.Conflict(str(_ci))
                r = _dc.reevaluare_sold(s["valoare_valuta"], s["curs_evidenta"],
                                        curs_bnr, s["tip"], str(s["cont"]))
                if r:
                    linii.append(r["linie"])
                    detalii.append({"cont": s["cont"], "curs_bnr": str(curs_bnr),
                                    "diferenta": str(r["diferenta"]["diferenta"]),
                                    "cont_rezultat": r["diferenta"]["cont"]})
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        if not linii:
            _d = _date.fromisoformat(str(corp["data"])[:10])
            return dict(_af.afirmatie(
                "fapt", "reevaluare valută", "nicio diferență de reevaluat",
                an=_d.year, luna=_d.month,
                temei_completitudine="soldurile în valută ale firmei, la cursul BNR din data cerută"),
                inregistrare_id=None, detalii=[], mesaj="nicio diferență de reevaluat")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_banca_ciorna(cur, schema, corp["data"], f"Reevaluare solduri valuta la {corp['data']} "
                                       "(OMFP 1802 pct. 316, curs BNR)")[0]
            for dd, cc, ss in linii:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "detalii": detalii}


def nota_leasing(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-leasing`; docstringul ei a ramas in stratul HTTP."""
    from core import leasing as _ls
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 212-217"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_credit(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-credit`; docstringul ei a ramas in stratul HTTP."""
    from core import credite as _cr
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_banca_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_avans(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-avans`; docstringul ei a ramas in stratul HTTP."""
    from core import avansuri as _av
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        dest = corp.get("destinatie", "stocuri")
        _OPERATII_AVANS = ("avans_platit", "regularizare_platit", "avans_incasat",
                           "regularizare_incasat")
        try:
            # [lotul 3] ORDINEA e reparatia: cota se cerea INAINTE de a se uita la operatie, deci
            # cine uita felul operatiunii — sau il scria gresit — afla despre cotă. Felul intai.
            if op not in _OPERATII_AVANS:
                raise ValueError(nomenclator_cerut("operatie", _OPERATII_AVANS))
            # [R149] Art. 291 alin. (6): *„In cazul schimbarii cotei se va proceda la
            # REGULARIZARE pentru a se aplica cota in vigoare la data LIVRARII de bunuri sau
            # prestarii de servicii"*. Deci la o regularizare cota nu se verifica pe data
            # regularizarii — se verifica pe data livrarii, care e chiar motivul pentru care
            # regularizarea exista: intre avans si livrare s-a schimbat cota.
            #
            # *O regularizare verificata pe data ei ar refuza exact cota pe care legea o cere.*
            _data_cota = corp.get("data")
            if op.startswith("regularizare"):
                _dl = corp.get("data_livrare")
                if not _dl:
                    raise ValueError(
                        "Data livrării/prestării e obligatorie la o regularizare: cota care se "
                        "regularizează e cea în vigoare ATUNCI, nu la data regularizării "
                        "(art. 291 alin. 6 Cod fiscal).")
                _data_cota = _dl
            cota = _common.cota_ceruta({**corp, "data": _data_cota})
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 282(2)b CF"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def achizitie_necorporala(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-necorporala`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    TIPURI = {"software":    ("208", "2808", 36),
              "licenta":     ("205", "2805", None),
              "brevet":      ("205", "2805", None),
              "dezvoltare":  ("203", "2803", None),
              "constituire": ("201", "2801", 60)}
    from core import anaf_api as _anaf
    # [P5 val 3] ANAF ÎNAINTE de conexiune — vezi nota de la `achizitie_taxare_inversa`.
    furnizor_cui = str(corp.get("furnizor_cui") or "").strip().upper().replace(" ", "")
    _tert_pl = _anaf.platitor_tva_freeze(furnizor_cui, fallback=True) if furnizor_cui else True
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        tip = corp.get("tip")
        if tip not in TIPURI:
            raise _erori.DateInvalide(nomenclator_cerut("tip", TIPURI))
        cont_imo, cont_am, dnf_regula = TIPURI[tip]
        dnf = corp.get("dnf_luni")
        if tip == "software":
            dnf = 36  # art. 28(9): programe informatice = 3 ani, fix
        elif tip == "constituire":
            dnf = min(int(dnf or 60), 60)  # art. 28(11): max 5 ani
        elif not dnf:
            raise _erori.DateInvalide(f"Durata normală de funcționare (luni) obligatorie pentru {tip} "
                                         "(durata contractului/de utilizare, art. 28(9))")
        from core import facturi_api as _fa
        try:
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                raise ValueError("Valoarea operațiunii trebuie să fie un număr mai mare "
                                 "decât zero.")
            cota = _common.cota_ceruta(corp)
            tva = (val * Decimal(str(cota)) / 100).quantize(Decimal("0.01"))
            if not furnizor_cui:      # calculat înaintea blocului; validarea rămâne aici
                raise ValueError("CUI furnizor obligatoriu (achizitia necorporala e factura de la furnizor)")
            numar = str(corp.get("numar") or "").strip()
            if not numar:
                raise ValueError("numar factura furnizor obligatoriu")
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(str(e) or "valoare invalidă")
        with conn.cursor() as cur:
            mfid = repo_mijloace_fixe.adauga(cur, schema, corp.get("cod") or f"NEC-{tip[:3].upper()}", corp["denumire"][:200], cont_imo, cont_am, val, int(dnf), corp["data"])[0]
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # rand FACTURA (achizitie normala de la furnizor RO cu CUI) -> D394 tip A. MF (mijloace_fixe) ramane
            # separat: factura = documentul de achizitie; imobilizarea = activul amortizabil (amortizare/D406).
            # `_tert_pl` s-a înghețat înaintea blocului (TVA deductibilă -> furnizor plătitor)
            fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                       linii=[{"descriere": corp["denumire"][:200], "cantitate": 1,
                                               "pret_unitar": str(val), "cota_tva": cota}],
                                       tert_nume=furnizor_nume or None, tert_cui=furnizor_cui, status="importata",
                                       tert_platitor_tva=_tert_pl)
            fid = fres["factura_id"]
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, f"Achizitie necorporala {tip}: {corp['denumire']}"
                                       f" (amortizare {dnf} luni, art. 28(9) CF)"[:200])[0]
            for dd, cc, ss in [(cont_imo, "404", val), ("4426", "404", tva)]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "mijloc_fix_id": mfid, "dnf_luni": int(dnf),
            "conturi": [cont_imo, cont_am]}


def _cere_amortizarea_inregistrata(conn, schema, cont_amortizare, ref, de_eliminat, denumire):
    """[R192] Reevaluarea nu poate elimina o amortizare pe care evidența n-a înregistrat-o.

    **DE CE E UN REFUZ, nu un avertisment.** Reevaluarea pe metoda valorii nete începe prin
    `28xx = 21x` cu amortizarea cumulată. Cifra aia vine din **registru** (motorul o calculează din
    PIF, durată și metodă); soldul contului vine din **notele chiar înregistrate**. Dacă registrul o
    ia înainte, nota ar scădea din cont o amortizare care nu există acolo — soldul `28xx` trece pe
    minus, iar valoarea rămasă a activului devine o **cifră validă și falsă**: se calculează, se
    afișează, pleacă în declarație, și nimic nu o contrazice.

    **Judecata și textul sunt PURE**, în `core/reevaluare.py`: aici rămâne doar citirea soldului.
    *Așa cifrele refuzului sunt DATE, iar o probă poate cere conținutul fără să caute cuvinte
    într-un șir.*

    Soldul e CREDITOR (credit − debit) la data reevaluării: debitele sunt chiar eliminările
    anterioare și ieșirile din evidență, deci trebuie scăzute.
    """
    from core import control_incrucisat as _ci
    from core import reevaluare as _rv
    r = _ci.rulaje_interval(conn, schema, "1900-01-01", ref.isoformat(), [cont_amortizare])
    v = r.get(cont_amortizare) or {}
    sold = (v.get("credit") or 0) - (v.get("debit") or 0)
    div = _rv.divergenta_amortizare(de_eliminat, sold)
    if div is None:
        return
    raise _erori.CerereGresita(
        _rv.mesaj_divergenta(div, denumire, cont_amortizare, ref.isoformat()))


def reevaluare_imobilizare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reevaluare-imobilizare`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import reevaluare as _rv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie", "reevaluare")
        try:
            fapt = None   # [R59] reevaluarea ca OBIECT, consemnata langa ciorna; `None` la surplus
            if op == "surplus":
                r = _rv.nota_realizare_surplus(corp["suma"])
                descr = "Transfer surplus reevaluare realizat (105=1175, pct.109-110)"
                extra = {}
            else:
                with conn.cursor() as cur:
                    mf = repo_mijloace_fixe.pentru_reevaluare(cur, schema, corp["mijloc_fix_id"])
                if not mf:
                    # [R147] „inexistent/inactiv" lasa omul sa ghiceasca pe care din doua.
                    raise _erori.Inexistent("Mijlocul fix ales nu există în registrul "
                                                 "firmei sau a fost casat. Alege-l din listă.")
                den, ci, ca, val, rez, dnf, pif, met, reev = mf
                ref = _date.fromisoformat(corp["data"])
                from core import d406_active as _d406
                mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                        "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif,
                        "metoda": met, "reevaluari": reev}
                amortizare = _d406.amortizat_la_data(mf_d, ref)["amortizat"]   # metoda reala, nu liniar
                _cere_amortizarea_inregistrata(conn, schema, ca, ref, amortizare, den)
                r = _rv.nota_reevaluare(val, amortizare, corp["valoare_justa"], ci, ca,
                                        corp.get("sold_105_activ", 0),
                                        corp.get("pierdere_655_anterioara", 0))
                descr = f"Reevaluare {den}: neta {r['valoare_neta']} -> justa "                         f"{corp['valoare_justa']} (OMFP 1802 pct.111-116)"
                extra = {"valoare_neta": str(r["valoare_neta"]),
                         "diferenta": str(r["diferenta"]), "amortizare_eliminata": str(amortizare)}
                # Valoarea justa se ia din MOTOR (neta + diferenta), nu din corpul cererii: asa
                # randul consemnat e exact cifra pe care s-au construit liniile notei. O a doua
                # citire a intrarii ar putea sa nu rotunjeasca la fel.
                fapt = {"mijloc_fix_id": corp["mijloc_fix_id"], "data": ref,
                        "valoare_bruta_veche": val, "amortizare_eliminata": amortizare,
                        "valoare_justa": r["valoare_neta"] + r["diferenta"]}
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            if fapt:
                # [R59] Efectul pe registru NU se produce aici: nota e CIORNA. Se consemneaza ce
                # propune ea, iar `mijloace_fixe.valoare` urca la VALIDARE (`jurnal_valideaza`).
                # *Altfel un `UPDATE` pe registrul care conduce amortizarea s-ar face dintr-o
                # propunere — chiar riscul numit in varianta (a) a conditiei de deblocare.*
                repo_reevaluari.consemneaza(
                    cur, schema, iid, fapt["mijloc_fix_id"], fapt["data"],
                    fapt["valoare_bruta_veche"], fapt["amortizare_eliminata"],
                    fapt["valoare_justa"])
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **extra}


def nota_provizion_ep(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-provizion`; docstringul ei a ramas in stratul HTTP."""
    from core import provizioane as _pv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 26 CF / OMFP 1802"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_productie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-productie`; docstringul ei a ramas in stratul HTTP."""
    from core import productie as _pr
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_obiect_inventar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-obiect-inventar`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import obiecte_inventar as _oi
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 / OUG 8/2026"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_asociati(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-asociati`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import decontari_asociati as _da
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0)
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_sponsorizare_ep(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-sponsorizare`; docstringul ei a ramas in stratul HTTP."""
    from core import sponsorizari as _sp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Sponsorizare (6582, nedeductibil, "
                 "credit fiscal art. 25(4)i)")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], "credit_fiscal": info}


def nota_subventie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-subventie`; docstringul ei a ramas in stratul HTTP."""
    from core import subventii as _sb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 392-402"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_chirie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-chirie`; docstringul ei a ramas in stratul HTTP."""
    from core import comodat_chirii as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        ids = []
        with conn.cursor() as cur:
            for d0, linii in note:
                descr = (corp.get("descriere") or d0)
                iid = repo_contabilitate.nota_facturi_ciorna_2(cur, schema, corp["data"], descr[:200])[0]
                ids.append(iid)
                for dd, cc, ss in linii:
                    repo_contabilitate.adauga_linie_2(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrari": ids, **info}


def nota_decont_deplasare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-decont-deplasare`; docstringul ei a ramas in stratul HTTP."""
    from core import deconturi as _dp
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 76(2)k CF / HG 714/2018"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_casa_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_bacsis(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-bacsis`; docstringul ei a ramas in stratul HTTP."""
    from core import bacsis as _bc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - Legea 376/2022"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_casa_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_sgr(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-sgr`; docstringul ei a ramas in stratul HTTP."""
    from core import sgr as _sg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - HG 1074/2021"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_perisabilitati(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-perisabilitati`; docstringul ei a ramas in stratul HTTP."""
    from core import perisabilitati as _pe
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _pe.calcul(corp["valoare_intrari"], corp["procent_limita"],
                           corp["pierdere_constatata"], _common.cota_ceruta(corp),
                           _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc", "371"),
                           bool(corp.get("degradare_dovedita_distrusa")))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or
                 f"Perisabilitati: limita {r['limita']}, deductibil {r['deductibil']}, "
                 f"nedeductibil {r['nedeductibil']} (PV inventariere)")[:200]
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr + " - HG 831/2004")[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "limita": str(r["limita"]),
            "deductibil": str(r["deductibil"]), "nedeductibil": str(r["nedeductibil"]),
            "ajustare_tva": str(r["ajustare_tva"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def nota_contract_special(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-contract-special`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_speciale as _cs
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _cs.nota(corp["brut"], corp.get("fel", "zilier"),
                         corp.get("sursa", "casa"), la_data=corp.get("data"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        fel = corp.get("fel", "zilier")
        descr = (corp.get("descriere") or
                 f"Remuneratie {fel} brut {corp['brut']} (net {r['net']})") +                 (" - L52/2011" if fel == "zilier" else " - art. 76(2)g/i CF")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_salarii_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "brut": str(r["brut"]), "cas": str(r["cas"]),
            "cass": str(r["cass"]), "impozit": str(r["impozit"]), "net": str(r["net"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def tenant_mijloace_fixe(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/mijloace-fixe`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from datetime import date as _date
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    azi = _date.today()
    out = []
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            rows = repo_mijloace_fixe.toate(cur)
    from core import d406_active as _d406
    for (mid, cod, den, ci, ca, val, rez, dnf, pif, met, activ, reev) in rows:
        val = Decimal(str(val or 0)); rez = Decimal(str(rez or 0))
        amortizat = ramas = eroare = None
        if activ:
            mf_d = {"cod": cod, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                    "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif,
                    "metoda": met, "reevaluari": reev}
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


def nota_inventariere(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-inventariere`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import inventariere as _iv
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
                        mf = repo_mijloace_fixe.pentru_inventariere(cur, schema, mf_id)
                    if not mf:
                        # [R147] „inexistent/inactiv" lăsa omul să ghicească pe care din două.
                        raise _erori.Inexistent("Mijlocul fix ales nu există în registrul "
                                                     "firmei sau a fost casat. Alege-l din listă.")
                    den, ci, ca, val, rez, dnf, pif, met, reev = mf
                    ref = _date.fromisoformat(corp["data"])
                    from core import d406_active as _d406
                    mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                            "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif,
                            "metoda": met, "reevaluari": reev}
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 2861/2009"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            if mf_id:
                repo_mijloace_fixe.scoate_din_evidenta(cur, schema, mf_id)
            mf_nou_id = None
            if op == "plus_mf":
                mf_nou_id = repo_mijloace_fixe.adauga_cu_reevaluare(cur, schema, mf_reg["cod"], mf_reg["denumire"], mf_reg["cont_imobilizare"], mf_reg["cont_amortizare"], mf_reg["valoare"], mf_reg["rezidual"], mf_reg["dnf_luni"], mf_reg["data_pif"], mf_reg["metoda"])[0]
        conn.commit()
    rez_out = {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}
    if mf_nou_id:
        rez_out["mijloc_fix_id"] = mf_nou_id
    return rez_out


def nota_lichidare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-lichidare`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import lichidare as _li
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 897/2015"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}


def nota_ong(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-ong`; docstringul ei a ramas in stratul HTTP."""
    from core import ong as _on
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
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
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or
                 f"Venit AFSP {corp.get('fel', 'cotizatie')} pe {r['cont_venit']}") +                 " - OMFP 3103/2017"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_casa_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "cont_venit": r["cont_venit"],
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}


def tenant_activare(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/activare`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not _uc_comun._acces_pentru_activare(conn, ctx["rol"], ctx.get("firm"), tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            return tenant_stergere.comuta_activ(conn, tenant_id, date.activ, ctx["uid"])
        except ValueError as e:
            raise _erori.CerereGresita(str(e))



def client_acces_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/client-acces`; docstringul ei a ramas in stratul HTTP."""
    email = (date.email or "").strip().lower()
    if not _uc_comun._email_valid(email):  # [R138] forma, nu doar prezenta unui @
        raise _erori.CerereGresita(EMAIL_INVALID)
    import secrets
    parola_temp = secrets.token_urlsafe(9)
    tok = "ml_" + secrets.token_urlsafe(32)   # [P4] se pregătește înainte: intră cu contul
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            _ex = repo_utilizatori.contul_dupa_email(cur, email)
            if _ex and (_ex["rol"] != "client" or _ex["activ"]):
                raise _erori.CerereGresita(EMAIL_EXISTA)
            # [R62 (2)] Aceeasi ramura de reactivare exista si aici. Gardul repara CLASA, nu
            # instanta: daca ar sta doar pe ruta clientului, calea prin cabinet ar ramane deschisa.
            _uc_comun._cere_acelasi_cabinet(_ex, ctx["firm"])
            if _ex:  # client_mesaj_v1: reinvitare client dezactivat
                uid = _ex["id"]
                repo_utilizatori.activeaza_contul_cu_nume(cur, date.nume or email.split("@")[0], uid)
                repo_utilizatori.leaga_contul_de_firma_idempotent(cur, uid, tenant_id)
            el_creaza = _ex is None
            if el_creaza:
                uid = repo_utilizatori.creeaza_cont(cur, email, _nucleu.hash_parola(parola_temp), date.nume or email.split("@")[0], ctx["firm"])["id"]
                repo_utilizatori.leaga_contul_de_firma(cur, uid, tenant_id)
            _uc_comun._urma_portal(cur, tenant_id, "acces_dat",
                         "cabinetul a dat acces la portal lui %s (utilizator #%s)" % (email, uid),
                         ctx["uid"])
            # [P4, 09.09.2026] TOKENUL INTRĂ CU CONTUL, ÎN ACEEAȘI TRANZACȚIE.
            #
            # Ce era până azi: contul de client (cu o parolă temporară pe care n-o știe nimeni) se
            # scria într-o tranzacție, iar tokenul de activare — singura lui cale de intrare — în
            # a doua. O eroare între ele lăsa un utilizator care NU poate intra niciodată, iar
            # urma din portal spunea „cabinetul a dat acces". Fundătură, și scrisă ca reușită.
            _uc_comun._pune_token(cur, tok, uid, "48 hours")
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#magic=" + tok
    _pm = ("<p style='border-left:3px solid #3d8fd6;padding-left:12px;color:#334155'>%s</p>" % date.mesaj.strip()) if (date.mesaj or "").strip() else ""  # client_mesaj_v1
    html = ("<p>Buna,</p>" + _pm + "<p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (d.get("nume", ""), link)
    _obs.trimite_email_html(email, "Acces portal iConta.eu — " + d.get("nume", ""), html)
    return {"ok": True, "user_id": uid}



def parteneri_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri/incarca`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    continut = continut
    try:
        randuri = solduri_parteneri_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    # [lotul 6] Un `.txt` cu o linie de proza intorcea `{"randuri": []}` — „fisierul n-are parteneri"
    # arata identic cu „fisierul n-a fost citit". A treia cale cu aceeasi gaura in lotul asta.
    if not randuri:
        raise _erori.DateInvalide("Din fișierul %s n-am putut citi niciun partener. Se așteaptă un "
                                 "CSV sau un XLSX cu solduri pe parteneri — un fișier necitit nu e "
                                 "un fișier gol." % (nume_fisier or "trimis",))
    td = round(sum(r["debit"] for r in randuri), 2)
    tc = round(sum(r["credit"] for r in randuri), 2)
    with db.get_conn(schema) as conn:
        coer = solduri_parteneri_api.coerenta(conn, randuri)
    erori = migrare_api.erori_verifica(solduri_parteneri_api.verifica_randuri(randuri))  # [Q5] poarta unica
    return _uc_comun._raspuns({"randuri": randuri, "total_debit": td, "total_credit": tc, "coerenta": coer, "erori": erori})



def salariati_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati-import/incarca`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    continut = continut
    try:
        randuri = salariati_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
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
    return _uc_comun._raspuns({"randuri": randuri, "total": len(randuri), "valizi": valizi,
            "invalizi": len(randuri) - valizi, "erori": erori})



def retete_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete-import/incarca`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    continut = continut
    try:
        retete = retete_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    with db.get_conn(schema) as conn:
        retete = retete_import_api.potriveste(conn, schema, retete)
    return _uc_comun._raspuns({"retete": retete, "rezumat": retete_import_api.rezumat(retete)})



def rip_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip-import/incarca`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    continut = continut
    try:
        date, raport = rip_migrare_api.extrage_operatiuni(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    ops = date.get("operatiuni", [])
    respinse = raport.get("respinse", [])
    if not ops and not respinse:
        raise _erori.CerereGresita("fișierul nu conține operațiuni de import")
    # import atomic (importa face commit/rollback propriu); erori DB -> nimic scris
    with db.get_conn(schema) as conn:
        rez = rip_migrare_api.importa(conn, schema, ops)
    if rez["erori"]:
        raise _erori.DateInvalide("import eșuat: " + str(rez["erori"][0].get("motiv", "eroare la scriere")))
    # marcheaza stratul rip (public.migrare_status, per cabinet) pentru reminder()
    with db.get_conn() as conn:
        if respinse:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "in_lucru",
                                       f"{len(respinse)} rânduri respinse la import — de completat")
        else:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "gata", "")
    return _uc_comun._raspuns({"importate": rez["importate"], "sarite_duplicat": rez.get("sarite_duplicat", 0), "raport": raport})



def factura_pdf_ruta(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/pdf`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
        if not f:
            raise _erori.Inexistent("factură inexistentă")
        profil = _fp.citeste_profil(conn)
    try:
        pdf = _pdf.genereaza_pdf(profil, f)
    except ValueError as e:
        # [bilant_422_v1] refuzul motivat al generatorului de PDF (ex. linie fara cota TVA)
        # ajungea la contabil ca 500 gol. Gasit de core/test_refuz_generator_422.py.
        raise _erori.DateInvalide(str(e))
    nume = "factura_" + str(f.get("numar") or factura_id).replace("/", "-") + ".pdf"
    return pdf, nume



def facturi_emite(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/emite`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._preincalzeste_cursul(date.moneda, date.data_emitere)   # [P5 val 3] descărcarea BNR, înainte de tranzacție
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    if not (date.tert_nume or "").strip():
        raise _erori.DateInvalide("Denumirea beneficiarului e obligatorie pe factură. Completeaz-o înainte de emitere.")
    with db.get_conn(schema) as conn:
        are_stoc = any(l.get("articol_id") for l in linii)
        # poarta doar la FACTURA (nu proforma/aviz), la firma CV cu linie de stoc
        poarta_ceruta = (date.tip == "factura") and are_stoc
        if poarta_ceruta and date.pleaca_marfa is None:
            raise _erori.DateInvalide("Raspunde la poarta: pleaca marfa acum? (DA descarca gestiunea / NU doar fiscal)")
        platitor = _uc_comun._platitor_tva_firma(conn)
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
            # [R139] Rezumatul poarta MOTIVELE, nu doar numele campurilor, si nu mai spune
            # „Completează" despre un camp care e completat gresit. Mesajele per camp ajung tot
            # langa casetele lor (api.js:41 -> eroareCamp); asta e doar rezumatul de deasupra.
            raise _erori.DateInvalide({"cod": "LINII_INCOMPLETE",
                "mesaj": "Liniile facturii nu sunt bune: " + "; ".join(
                    "%s — %s" % (x["eticheta"], x.get("mesaj") or "") for x in e.campuri),
                "campuri": e.campuri})
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        # descarcare gestiune DOAR la poarta = DA, in ACEEASI tranzactie (atomic: emit + descarcare)
        if poarta_ceruta and date.pleaca_marfa is True and isinstance(r, dict) and r.get("factura_id"):
            from core import stocuri_cv_api as _cv
            from datetime import date as _dt_date  # fix F821: datetime neimportat in scope (date = param Pydantic)
            r["descarcare"] = _cv.descarca_factura(conn, schema, r["factura_id"],
                                                   date.data_emitere or _dt_date.today().isoformat())
    # [lot 2] moneda inexistenta e o INTRARE gresita (422), nu un conflict temporar (409):
    # 409 cu „reincearca / manual" ii promitea contabilului ca mai tarziu ar merge.
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "MONEDA_NECOTATA":
        raise _erori.DateInvalide(r)
    # [R130] Cursul e mai vechi decat pragul: emiterea AUTOMATA se opreste, facturarea NU. `409`,
    # cu iesirea numita in corp (curs manual + data lui) — un refuz fara iesire ar fi interdictia 47.
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "CURS_PREA_VECHI":
        raise _erori.Conflict(r)
    # curs BNR indisponibil -> 409 cu detaliile pt frontend (Reincearca / Manual)
    if isinstance(r, dict) and r.get("ok") is False and r.get("cod") == "CURS_INDISPONIBIL":
        raise _erori.Conflict(r)
    return r



def proforma_transforma(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/transforma`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [P5 val 3] Moneda se citeste intr-o tranzactie SCURTA, apoi cursul se aduce — amandoua
    # inaintea tranzactiei de emitere, ca descarcarea BNR sa nu tina o conexiune din pool.
    import datetime as _dtx
    _uc_comun._preincalzeste_cursul(_uc_comun._moneda_facturii(schema, factura_id), _dtx.date.today())
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = repo_facturi.tip_si_transformare(cur, factura_id)
        if not r:
            raise _erori.Inexistent("document inexistent")
        if r[0] == "factura":
            raise _erori.DateInvalide("documentul e deja factura")
        if r[1]:
            raise _erori.Conflict(f"deja transformat in factura #{r[1]}")
        f = facturi_api.detalii_factura(conn, factura_id)
        linii = [{"descriere": l.get("descriere"), "cantitate": l.get("cantitate"),
                  "pret_unitar": l.get("pret_unitar"), "cota_tva": l.get("cota_tva")}
                 for l in (f.get("linii") or [])]
        platitor = _uc_comun._platitor_tva_firma(conn)
        try:
            rez = facturi_api.emite_factura(conn, linii, client_id=f.get("client_id"),
                tert_nume=f.get("tert_nume"), tert_cui=f.get("tert_cui"),
                moneda=f.get("moneda") or "RON", platitor_tva=platitor)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            repo_facturi.leaga_proforma_de_factura(cur, rez["factura_id"], factura_id)
        conn.commit()
    return rez



def salarii_contare_scrie(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salarii-contare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from datetime import date as _date
    from core import salarii_contare as _sc
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (a)] Nota poarta ultima zi a lunii declarate; intr-o luna inchisa nu se scrie.
        ultima = _date(an, luna, 28)
        _uc_comun._cere_luna_deschisa(conn, schema, ultima)
        try:
            p = _sc.propunere(conn, schema, an, luna)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            r = repo_contabilitate.id_nota_dupa_numar_2(cur, p["document_ref"])
            if r:
                return {**p, "deja_contata": True, "nota_id": r[0],
                         "cod": "DEJA_CONTATA"}
            # Statusul e PARAMETRU, nu text in SQL: asa se poate asertaza pe structura ca nota
            # intra CIORNA (patru-ochi), nu cautand `'ciorna'` intr-un sir (METODA §23).
            nota_id = repo_contabilitate.nota_cu_sursa_si_status(cur, ultima, p["document_ref"], "Stat de plata %02d/%d" % (luna, an), "salarii", _uc_comun.STARE_CIORNA)[0]
            for n in p["note"]:
                repo_contabilitate.adauga_linie_fara_schema(cur, nota_id, n["debit"], n["credit"], n["suma"])
        conn.commit()
    return {**p, "deja_contata": True, "nota_id": nota_id, "cod": "CONTATA"}



def horeca_import_amef(tenant_id, continut, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/horeca/import-amef`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal as D
    from core import amef_import as _am
    continut = continut
    try:
        xml = _am.extrage_xml(continut)
        rz = _am.parseaza_raport_z(xml)
    except (ValueError, Exception) as e:
        raise _erori.DateInvalide(f"fisier AMEF invalid: {e}")
    if not rz["data"]:
        raise _erori.DateInvalide("nu am putut extrage data din idR")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        # [R61] Poarta de perioada lipsea DOAR aici, iar asta era pe dos: ruta fara rol era si
        # cea fara poarta. O nota intr-o luna inchisa e aceeasi clasa indiferent ca e ciorna.
        _uc_comun._cere_luna_deschisa(conn, schema, rz["data"])
        numerar = sum((p["suma"] for p in rz["plati"] if p["tip"] == "numerar"), D("0"))
        rest = sum((p["suma"] for p in rz["plati"] if p["tip"] != "numerar"), D("0"))
        with conn.cursor() as cur:
            _numar_z = f"Z-{rz['nui']}-{rz['nr_raport']}"
            _uc_comun._cere_z_unic(cur, schema, _numar_z)
            # [P5 val 1b] Verificarea de mai sus e calea RAPIDĂ, cea care dă omului un mesaj
            # care se poate citi. Indexul unic e plasa de dedesubt, pentru cursa dintre două
            # cereri simultane — acum posibilă, fiindcă ruta rulează pe un fir. Violarea lui
            # produce ACELAȘI refuz, nu un `500`: *o cursă pierdută și o a doua încercare
            # conștientă trebuie să arate la fel pentru cel care operează casa de marcat.*
            try:
                tranzactie.savepoint_z_insert(cur)
                # id-ul se citește ÎNAINTE de `RELEASE`: orice `execute` următor golește cursorul
                iid = repo_contabilitate.nota_amef_ciorna(cur, schema, rz["data"], _numar_z, f"Raport Z {rz['data']} AMEF {rz['nui']} nr {rz['nr_raport']} ({rz['nr_bonuri']} bonuri) - de verificat cu Z tiparit")[0]
                tranzactie.elibereaza_z_insert(cur)
            except _psycopg2.errors.UniqueViolation:
                tranzactie.intoarce_la_z_insert(cur)
                _uc_comun._cere_z_unic(cur, schema, _numar_z)   # ridică 409, cu documentul existent numit
                raise                                  # dacă totuși nu l-a găsit, nu înghițim
            linii = []
            if numerar: linii.append(("5311", "707", numerar))
            if rest: linii.append(("5125", "707", rest))
            for cota in rz["cote"]:
                if cota["tva"]:
                    linii.append(("707", "4427", cota["tva"]))
            for deb, cred, suma in linii:
                repo_contabilitate.adauga_linie_4(cur, schema, iid, deb, cred, suma)
        conn.commit()
    return {"inregistrare_id": iid, "status": "ciorna", "data": rz["data"],
            "total": str(rz["total"]), "tva_total": str(rz["total_tva"]),
            "cote": [{"cota": x["cota"], "tva": str(x["tva"])} for x in rz["cote"]],
            "numerar": str(numerar), "card_altele": str(rest)}



def horeca_raport_z(tenant_id, rz, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/horeca/raport-z`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, rz.data)   # [R42 (a)] nota poartă data raportului Z
        nui = (rz.nui or "").strip()
        nr_raport = (rz.nr_raport or "").strip()
        if not nui or not nr_raport:
            raise _erori.CerereGresita(MESAJ_Z_FARA_CHEIE)
        numar = "Z-%s-%s" % (nui, nr_raport)
        total = D(str(rz.total_11)) + D(str(rz.total_21))
        if total <= 0:
            raise _erori.CerereGresita("totalul pe cote trebuie să fie pozitiv")
        if abs(float(total) - (rz.numerar + rz.card)) > 0.01:
            raise _erori.CerereGresita("numerar + card trebuie să fie egal cu totalul pe cote")
        # suta marita: TVA = total * cota / (100 + cota)
        tva11 = (D(str(rz.total_11)) * 11 / 111).quantize(D("0.01"))
        tva21 = (D(str(rz.total_21)) * 21 / 121).quantize(D("0.01"))
        baza11 = D(str(rz.total_11)) - tva11
        baza21 = D(str(rz.total_21)) - tva21
        with conn.cursor() as cur:
            _uc_comun._cere_z_unic(cur, schema, numar)
            iid = repo_contabilitate.nota_horeca_z_validata(cur, schema, rz.data, numar, "Raport Z %s casa %s nr %s" % (rz.data, nui, nr_raport))[0]
            linii = []
            if rz.numerar: linii.append(("5311", "707", rz.numerar))
            if rz.card: linii.append(("5125", "707", rz.card))
            # corectie TVA: 707 -> 4427 pentru TVA colectata
            tva_total = tva11 + tva21
            if tva_total: linii.append(("707", "4427", float(tva_total)))
            for deb, cre, suma in linii:
                repo_contabilitate.adauga_linie_3(cur, schema, iid, deb, cre, suma)
    return {"ok": True, "nota_id": iid,
            "tva_11": float(tva11), "tva_21": float(tva21),
            "baza_11": float(baza11), "baza_21": float(baza21)}



def tenant_fluturas(tenant_id, salariat_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/fluturas/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import stat_plata_api as _sp
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        cur = conn.cursor()
        nf = (repo_tenants.nume_dupa_id(cur, tenant_id) or [""])[0]
    with db.get_conn(schema) as conn:  # fluturas_pdf foloseste nume necalificate -> search_path pe tenant
        pdf = _sp.fluturas_pdf(conn, schema, salariat_id, an, luna, nf)
    if pdf is None:
        raise _erori.Inexistent("salariat inexistent")
    return pdf



def tenant_stat_emite(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata/emite`; docstringul ei a ramas in stratul HTTP."""
    from core import stat_plata_emis as _spe
    # ORDINEA: acces (404) -> drept (403) -> validarea corpului (422). Prima forma citea `corp["an"]`
    # INAINTE de verificarea accesului: un strain primea KeyError -> 500, adica invata ca ruta exista
    # si ce campuri asteapta. Prins de gardul de izolare structurala, care probeaza fiecare ruta noua
    # {tenant_id} cu corp gol.
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    an, luna = _uc_comun._cere_an_luna(corp)
    with db.get_conn(schema) as conn:
        _spe.aplica(conn, schema)
        emise = _spe.emite(conn, schema, an, luna, de_cine=str(ctx["uid"]))
        return {"emise": len(emise), "total": len(_spe.citeste(conn, schema, an, luna))}



def tenant_stat_corectie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata/corectie`; docstringul ei a ramas in stratul HTTP."""
    from core import stat_plata_emis as _spe
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    if not _uc_comun._are_permisiune(ctx, "poate_valida"):
        raise _erori.FaraDrept(FARA_DREPT_VALIDARE)
    an, luna = _uc_comun._cere_an_luna(corp)
    try:
        sid = int(corp["salariat_id"])
    except (KeyError, TypeError, ValueError):
        raise _erori.DateInvalide("cererea nu spune pentru care salariat se face corecția")
    with db.get_conn(schema) as conn:
        try:
            return _spe.corectie(conn, schema, sid, an, luna, de_cine=str(ctx["uid"]))
        except ValueError as e:
            raise _erori.Conflict(str(e))



def tenant_plata_salarii_fisier(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/plata-salarii-fisier`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 10] `luna=13` raspundea „month must be in 1..12" — mesajul
                               # bibliotecii, in engleza, ajuns pana la contabil.
    from core import plata_salarii as _ps
    from core import artefacte as _art
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        cur = conn.cursor()
        nf = (repo_tenants.nume_dupa_id_3(cur, tenant_id) or [""])[0]
    with db.get_conn(schema) as conn:  # genereaza_pain001 foloseste nume necalificate -> search_path pe tenant
        try:
            xml, meta = _ps.genereaza_pain001(conn, schema, an, luna, nume_firma_fallback=nf)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        _art.pastreaza(conn, schema, "plata_salarii", "%04d-%02d" % (an, luna), xml,
                       produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return xml, meta



def tenant_adeverinta(tenant_id, salariat_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}/adeverinta`; docstringul ei a ramas in stratul HTTP."""
    from core import adeverinta as _adv
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            pdf = _adv.pdf(conn, schema, salariat_id, date.dict())
        except ValueError as e:   # [R66 (c)] refuzul numeste documentul si unde se completeaza
            raise _erori.DateInvalide(str(e))
    if pdf is None:
        raise _erori.Inexistent("salariat inexistent")
    return pdf



def cabinet_bon_imagine(tenant_id, bon_id, n, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/{bon_id}/imagine/{n}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    cale = _uc_comun._bon_imagine_cale(schema, bon_id, n)
    if not cale:
        raise _erori.Inexistent("imagine inexistentă")
    return cale



def chitanta_pdf(tenant_id, chitanta_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/chitante/{chitanta_id}/pdf`; docstringul ei a ramas in stratul HTTP."""
    from core import chitante as _ch
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_casa.chitanta_pentru_pdf(cur, schema, chitanta_id)
        if not r:
            raise _erori.Inexistent("chitanță inexistentă")
        te = repo_tenants.nume_si_cui(cur, tenant_id) or (None, None)
    pdf = _ch.pdf_chitanta({"nume": te[0], "cui": te[1]},
                           {"serie": r[0], "numar": r[1],
                            "data": data_ro(r[2]),
                            "client_nume": r[3], "client_cui": r[4], "suma": float(r[5] or 0),
                            "reprezentand": r[6]})
    return pdf, r



def cabinet_documente_balanta(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/documente/balanta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + detalii pe conn public
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    with db.get_conn(schema) as conn:  # balanta_pdf foloseste nume necalificate -> search_path pe tenant
        pdf = documente_api.balanta_pdf(conn, schema, an, luna, (d or {}).get("nume") or "")
    return pdf



def banca_rec_import(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/import`; docstringul ei a ramas in stratul HTTP."""
    from core import banca_parser, banca as _bk, reconciliere_api as _rec
    continut = continut
    try:
        tranzactii = banca_parser.parse_extras(continut, nume_fisier or "")
    except Exception as e:
        raise _erori.CerereGresita(f"nu am putut citi extrasul: {e}")
    for t in tranzactii:
        r = _bk.regula_cont({"sens": "debit" if t["suma"] < 0 else "credit",
                             "suma": abs(t["suma"]), "descriere": t.get("detalii", "")})
        t["cui"], t["tip"], t["nota"] = r.get("cui"), r.get("tip"), r.get("nota")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        return _uc_comun._raspuns({"linii": _rec.importa_extras(conn, schema, tranzactii, nume_fisier or "")})



def contracte_genereaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/genereaza`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            pdf = _ct.genereaza_pdf(conn, schema, corp.get("sablon_id"), corp)
        except ValueError as e:   # [R66 (c)]
            raise _erori.DateInvalide(str(e))
    if pdf is None:
        raise _erori.Inexistent("sablon inexistent")
    return pdf



def export_saga_factura(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/export-saga`; docstringul ei a ramas in stratul HTTP."""
    from core import export_saga as _xs
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        date_f = _xs.date_factura(conn, schema, factura_id)
    if date_f is None:
        raise _erori.Inexistent("factură inexistentă sau nu e emisă")
    firma, factura, linii = date_f
    xml = _xs.xml_factura(firma, factura, linii)
    nume = _xs.nume_fisier(firma.get("cui"), factura.get("numar"), factura.get("data_emitere"))
    return xml, nume



def export_saga_luna(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/export-saga`; docstringul ei a ramas in stratul HTTP."""
    from core import export_saga as _xs
    from core import artefacte as _art
    import io as _io, zipfile as _zip
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        ids = _xs.facturi_emise_luna(conn, schema, an, luna)
        if not ids:
            raise _erori.Inexistent("nicio factură emisă în luna aleasă")
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
    return buf, nume_zip



def export_winmentor_luna(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/export-winmentor`; docstringul ei a ramas in stratul HTTP."""
    from core import export_winmentor as _wm
    from core import artefacte as _art
    import io as _io, zipfile as _zip
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        try:
            fisiere = _wm.export_luna(conn, schema, an, luna)
        except ValueError as e:  # caracter neencodabil cp1250 -> nu scrie byte gresit tacit
            raise _erori.DateInvalide(str(e))
    if not fisiere:
        raise _erori.Inexistent("nicio factură emisă în luna aleasă")
    buf = _io.BytesIO()
    with _zip.ZipFile(buf, "w", _zip.ZIP_DEFLATED) as z:
        for nume, continut in fisiere.items():
            z.writestr(nume, continut)
    nume_zip = "export_winmentor_%04d_%02d.zip" % (an, luna)
    # [R45] Arhiva se pastreaza intreaga (base64), amprenta pe octetii ei.
    with db.get_conn() as _c:
        _art.pastreaza(_c, schema, "export_winmentor", "%04d-%02d" % (an, luna), buf.getvalue(),
                       produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return buf, nume_zip



def jurnal_creeaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal`; docstringul ei a ramas in stratul HTTP."""
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        return _uc_comun._jurnal_rez(_j.creeaza(conn, schema, corp.get("descriere"), corp.get("data"), corp.get("linii")))



def jurnal_editeaza(tenant_id, nota_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        return _uc_comun._jurnal_rez(_j.editeaza(conn, schema, nota_id,
                                       corp.get("descriere"), corp.get("data"), corp.get("linii")))



def jurnal_sterge(tenant_id, nota_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        return _uc_comun._jurnal_rez(_j.sterge(conn, schema, nota_id))



def jurnal_dezleaga(tenant_id, nota_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}/dezleaga`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    motiv = (corp.get("motiv") or "").strip()
    if not motiv:
        from core import afirmatii as _af
        raise _erori.DateInvalide(dict(_af.afirmatie(
            "neconformitate", "MOTIV_OBLIGATORIU",
            "Scrie motivul dezlegării: actul repară o potrivire greșită, iar peste șase luni "
            "urma fără motiv nu mai spune dacă a fost o eroare sau o scăpare.",
            unde="nota #%s" % nota_id, regula="dezlegarea unei note poartă motivul"),
            cod="MOTIV_OBLIGATORIU"))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        # P15, prin helperul canonic — același pe care îl cheamă editarea, ștergerea și validarea
        # unei note care există. Dezlegarea schimbă soldul facturii, deci e o modificare a lunii.
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        try:
            with _cf.cursor_dict(conn) as cur:
                fid = _cf.dezleaga_nota(cur, schema, nota_id)
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "NOTA_INEXISTENTA":
                raise _erori.Inexistent(e.mesaj)
            raise _erori.DateInvalide(e.mesaj)
        _uc_comun._urma_dezlegare(conn, ctx.get("uid"), tenant_id, nota_id, fid, motiv)
        conn.commit()
    # Fără cheie de revendicare în răspuns (`motiv` e una): afirmațiile despre datele firmei sunt
    # obiecte tipate, iar aici motivul e ecoul intrării, nu o afirmație a aplicației. Urma îl poartă.
    return {"ok": True, "nota_id": nota_id, "factura_id_dezlegata": fid}



def jurnal_valideaza(tenant_id, nota_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}/valideaza`; docstringul ei a ramas in stratul HTTP.

    [R59] Validarea e momentul in care o propunere devine EVIDENTA — deci si momentul in care
    efectul unei reevaluari intra pe registrul mijloacelor fixe (varianta (a) din conditia de
    deblocare a lui R59: *„ruta actualizeaza `mijloace_fixe` la validarea notei"*). Aceeasi
    tranzactie ca validarea: ori nota e validata SI registrul urcat, ori niciuna.
    """
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        rez = _j.valideaza(conn, schema, nota_id)
        if isinstance(rez, dict) and rez.get("ok"):
            _aplica_reevaluarea(conn, schema, nota_id)
        return _uc_comun._jurnal_rez(rez)


def _aplica_reevaluarea(conn, schema, nota_id):
    """[R59] Daca nota validata poarta o reevaluare neaplicata, urca valoarea bruta pe registru.

    Intoarce `True` daca a aplicat ceva. Nota fara reevaluare -> `False`, tacut: cele mai multe
    note n-au nicio legatura cu mijloacele fixe.

    IDEMPOTENT prin DATE, nu prin grija apelantului: randul se citeste cu `aplicata_la IS NULL` si
    `FOR UPDATE`, iar indexul unic pe `inregistrare_id` inchide si cazul in care s-ar consemna doua.
    *O a doua validare a aceleiasi note ar urca valoarea inca o data — si nimic n-ar spune.*
    """
    with conn.cursor() as cur:
        rand = repo_reevaluari.neaplicata_pentru_nota(cur, schema, nota_id)
        if not rand:
            return False
        rid, mijloc_fix_id, valoare_justa = rand
        repo_mijloace_fixe.urca_valoarea(cur, schema, mijloc_fix_id, valoare_justa)
        repo_reevaluari.marcheaza_aplicata(cur, schema, rid)
    return True



def d406_active_xml(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d406-active`; docstringul ei a ramas in stratul HTTP."""
    from core import d406_active as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            # [R190, etapa 2 lotul I, 15.09.2026] ORDINEA: se cer RANDURILE, abia apoi coloanele.
            # `cur.description` descrie ultima interogare EXECUTATA — iar cea care o executa e chiar
            # apelul la depozit. Pana azi linia de coloane sta deasupra apelului, deci `description`
            # era `None` si ruta raspundea `500` la ORICE cerere. Nu de la o zi anume: de la valul V1
            # al lui P7 (`8d182afa`), care a mutat `cur.execute` in depozit si a lasat linia unde
            # era. N-a prins-o nicio garda fiindca ruta n-are apelant (R70) — prima apasare pe ea a
            # fost proba lantului. Masurat: singura instanta din repo; celelalte patru locuri cu
            # `cur.description` au ordinea corecta (`artefacte`, `salariati_api`, `gdpr_export`,
            # `stat_plata_emis`).
            randuri = repo_mijloace_fixe.active_pentru_d406(cur, schema, an)
            cols = [d[0] for d in cur.description]
            lista = [dict(zip(cols, r)) for r in randuri]
    if not lista:
        raise _erori.Inexistent("niciun mijloc fix cu PIF până în anul cerut")
    try:
        xml = _m.xml_assets(lista, an)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    return xml



def d406_stocuri_xml(tenant_id, data_start, data_end, cui, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/d406-stocuri`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import d406_stocuri as _m
    try:
        ds, de = _date.fromisoformat(data_start), _date.fromisoformat(data_end)
    except ValueError:
        # [lotul 6] „date format YYYY-MM-DD" nu spunea CARE dintre cele doua e gresita.
        raise _erori.DateInvalide("Datele de început și de sfârșit se scriu ca AAAA-LL-ZZ, cu zile "
                                 "care există în calendar — am primit %r și %r."
                                 % (data_start, data_end))
    # [lotul 6] Un interval INVERSAT producea un XML SAF-T, adica un fisier oficial despre o
    # perioada care nu exista. Raportul se cere pe un interval, iar un interval are o ordine.
    if de < ds:
        raise _erori.DateInvalide("Sfârșitul perioadei (%s) e înaintea începutului (%s). "
                                 "Raportul se cere pe un interval, iar intervalul are o ordine."
                                 % (de.isoformat(), ds.isoformat()))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            rows = repo_stocuri.miscari_pentru_d406(cur, schema, de)
    grupat = {}
    for aid, den, um, cont, data, tip, cant, val in rows:
        art, mis = grupat.setdefault(aid, ({"id": aid, "denumire": den, "um": um,
                                            "cont_stoc": cont}, []))
        mis.append({"data": data, "tip": tip, "cantitate": cant, "valoare": val})
    try:
        xml = _m.xml_physical_stock(list(grupat.values()), ds, de, cui)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    return xml



def factura_primita_valideaza(tenant_id, primita_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    from core import contare_facturi as _cf
    cont = (corp.get("cont") or "").strip()
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            r = repo_efactura.primita_pentru_validare(cur, schema, primita_id)
            if not r:
                raise _erori.Inexistent("factură primită inexistentă")
            status, xmlb, cifb, fid_ex = r
            if status == "validata":          # idempotent - nu crea a doua cheltuiala
                return {"stare": "deja_validata", "factura_id": fid_ex}
            if status == "respinsa":
                raise _erori.Conflict("factura a fost respinsa; nu se poate valida")
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
                raise _erori.DateInvalide(dict(_af.afirmatie(
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
                raise _erori.DateInvalide("XML neparsabil: %s" % str(e)[:200])
            fid, _nou = _uc_comun._factura_din_parsat(cur, schema, f)   # leaga si factura existenta (dedup)
            fid_final = repo_efactura.marcheaza_primita_validata(cur, schema, fid, cont or None, primita_id)[0]
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
                repo_facturi.actualizeaza_clasificarea(cur, schema, _sets, _vals)
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



def decontare_valuta(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/decontare-valuta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._preincalzeste_cursul(corp.get("moneda", "EUR"), corp.get("data"))   # [P5 val 3] descărcarea BNR, înainte de tranzacție
    from datetime import date as _date
    from core import diferente_curs as _dc
    from core import curs_bnr as _cb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            data = _date.fromisoformat(corp["data"])
            try:
                curs_dec, _dcurs, _sursa = _cb.curs_pentru(conn, corp.get("moneda", "EUR"), data)
            except _cb.MonedaNecotata as _mn:   # [lotul 8] iesea ca `500`
                raise _erori.DateInvalide(str(_mn))
            except _cb.CursIndisponibil as _ci:
                raise _erori.Conflict(str(_ci))
            r = _dc.nota_decontare(corp["valoare_valuta"], corp["curs_evidenta"],
                                   curs_dec, corp["tip"],
                                    _cv.cere_cont(conn, schema, corp.get("cont_tert"), "cont_tert"),
                                   _cv.cere_cont(conn, schema, corp.get("cont_banca"), "cont_banca", "5124"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        d = r["diferenta"]
        descr = (corp.get("descriere") or "Decontare valuta") +                 f" {corp['valoare_valuta']} {corp.get('moneda','EUR')} curs {curs_dec}" +                 (f", dif. {d['sens']} {bani(d['diferenta'], 'lei')} ({d['cont']})" if d["cont"] else "")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_banca_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return {"inregistrare_id": iid, "curs_decontare": str(curs_dec),
            "lei_evidenta": str(r["lei_evidenta"]),
            "diferenta": {"suma": str(d["diferenta"]), "cont": d["cont"],
                          "sens": d["sens"]}}


def factura_email(tenant_id, factura_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/email`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    email = (date.email or "").strip()
    if not _uc_comun._email_valid(email):  # [R138] acelasi criteriu ca peste tot, nu unul propriu
        raise _erori.DateInvalide(EMAIL_INVALID)
    with db.get_conn(schema) as conn:
        f = facturi_api.detalii_factura(conn, factura_id)
        if not f:
            raise _erori.Inexistent("factură inexistentă")
        profil = _fp.citeste_profil(conn)
    import base64 as _b64
    try:
        pdf = _pdf.genereaza_pdf(profil, f)
    except ValueError as e:
        # [bilant_422_v1] refuzul motivat al generatorului de PDF (ex. linie fara cota TVA)
        # ajungea la contabil ca 500 gol. Gasit de core/test_refuz_generator_422.py.
        raise _erori.DateInvalide(str(e))
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
        raise _erori.ServiciuStrainCazut("trimiterea email a eșuat")
    return {"ok": True, "email": email}



def reges_trimite_salariat(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reges-trimite-salariat`; docstringul ei a ramas in stratul HTTP."""
    from core import reges_client as _rg
    import uuid as _uuid
    # ── [P5 val 3, 11.09.2026] FAZA 1: citirile ─────────────────────────────────────────
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            chei = repo_salariati.chei_reges(cur, tenant_id)
            if not chei:
                raise _erori.DateInvalide("chei REGES neconfigurate - folosește reges-config")
            s = repo_salariati.identitate_pentru_reges(cur, schema, corp["salariat_id"])
            if not s:
                raise _erori.Inexistent("salariat inexistent")
    mid = _uuid.uuid4()
    xml = _rg.mesaj_inregistrare_salariat(
        {"cnp": s[0], "nume": s[1], "prenume": s[2], "adresa": corp.get("adresa")},
        str(chei[3]), chei[0], message_id=mid)
    cl = _rg.RegesClient(chei[0], chei[1], chei[2])
    # ── APELUL EXTERN, fără nicio conexiune (token 30 s + POST 60 s) ────────────────────
    try:
        status, rasp = cl.trimite_salariat(xml)
    except Exception as e:
        raise _erori.ServiciuStrainCazut(f"REGES: {e}")
    # ── FAZA 2: tranzacție scurtă. NECONDIȚIONAT — salariatul e deja la REGES, iar rândul
    #    ăsta e urma lui. Dacă l-am condiționa de o revalidare, am putea pierde dovada unui
    #    act deja petrecut. Aceeași clasă cu rotația de token: efectul e SURSA valorii. ────
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            rid = repo_salariati.scrie_mesaj_reges(cur, tenant_id, corp["salariat_id"], str(mid), None, rasp[:4000])[0]
        conn.commit()
    return {"mesaj_id": rid, "http_status": status, "raspuns": rasp[:500]}



def reges_poll(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reges-poll`; docstringul ei a ramas in stratul HTTP."""
    from core import reges_client as _rg
    import re as _re
    # ── [P5 val 3, 11.09.2026] FAZA 1: citirile ─────────────────────────────────────────
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            chei = repo_salariati.chei_reges_fara_autor(cur, tenant_id)
            if not chei:
                raise _erori.DateInvalide("chei REGES neconfigurate")
    cl = _rg.RegesClient(chei[0], chei[1], chei[2])
    # ── APELUL EXTERN, fără conexiune. `poll_mesaj` CONSUMĂ un mesaj din coada REGES —
    #    ireversibil, deci ce urmează nu se poate condiționa de nicio revalidare. ─────────
    try:
        status, rasp = cl.poll_mesaj()
    except Exception as e:
        raise _erori.ServiciuStrainCazut(f"REGES: {e}")
    m_mid = _re.search(r"<(?:Initial)?MessageId>([0-9a-f-]{36})", rasp)
    m_rs = _re.search(r"ReferintaSalariat>?\s*<Id>([0-9a-f-]{36})", rasp)
    m_rc = _re.search(r"ReferintaContract>?\s*<Id>([0-9a-f-]{36})", rasp)
    # ── FAZA 2: tranzacție scurtă, necondiționat ────────────────────────────────────────
    with db.get_conn() as conn:
        if m_mid:
            with conn.cursor() as cur:
                repo_salariati.scrie_raspunsul_reges(cur, rasp[:4000], m_rs.group(1) if m_rs else None, m_rc.group(1) if m_rc else None, m_mid.group(1), tenant_id)
            conn.commit()
    return {"http_status": status, "raspuns": rasp[:1000]}



def verifica_vies_ep(tenant_id, cod_tva, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/verifica-vies`; docstringul ei a ramas in stratul HTTP."""
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("tenant inexistent sau fără acces")
    try:
        return _ic.verifica_vies(cod_tva)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    except Exception as e:
        raise _erori.ServiciuStrainCazut(f"VIES indisponibil: {e}")



def vanzare_ic(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-ic`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    # ── [P5 val 3, 11.09.2026] FAZA 1: citirile, fără nimic extern ──────────────────────
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
    # [lotul 8, 04.09.2026] Citirea campului era INAUNTRUL `try`-ului care prinde `Exception`,
    # deci un camp lipsa iesea ca „VIES indisponibil: 'cod_tva_client'" — o afirmatie falsa
    # despre un serviciu extern, cu numele campului intre ghilimele simple. *Ce nu s-a trimis
    # nu se afla de la VIES.*
    _cod_client = str(corp.get("cod_tva_client") or "").strip()
    if not _cod_client:
        raise _erori.DateInvalide("Lipsește codul de TVA al clientului. Fără el livrarea "
                                 "intracomunitară nu se poate verifica în VIES și nu ajunge "
                                 "în D390.")
    # ── I/O EXTERN, fără nicio conexiune în mână (termen 15 s) ──────────────────────────
    try:
        v = _ic.verifica_vies(_cod_client)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    except Exception as e:
        raise _erori.ServiciuStrainCazut(f"VIES indisponibil: {e}")
    # ── FAZA 2: tranzacție scurtă, cu REVALIDARE înainte de orice scriere ───────────────
    # Ce s-ar fi putut schimba în cele 15 s: accesul revocat, luna închisă de altcineva. Se cer
    # din nou, amândouă, iar la refuz iese exact eroarea de azi — rezultatul VIES se aruncă.
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            # [R186/R187, 16.09.2026] TIPUL se valideaza contra nomenclatorului, nu se citeste cu
            # `== "servicii"`: axa se INGHEATA pe document, deci o valoare gresita ar ingheta o
            # minciuna. Pana azi orice altceva decat „servicii" devenea TACIT bunuri — aceeasi clasa
            # pe care lotul 5 a reparat-o la `achizitie_ic` pe 04.09.
            if corp.get("tip") not in ("bunuri", "servicii"):
                raise ValueError(nomenclator_cerut("tip", "bunuri|servicii"))
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
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                raise ValueError("Valoarea operațiunii trebuie să fie un număr mai mare "
                                 "decât zero.")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Vanzare IC") + " - " + ment +                 f" [{v['nume']}]"
        # [R187, decizia lui Costin 16.09.2026] LIVRAREA PRODUCE FACTURA. Fara rand in `facturi`,
        # operatiunea nu putea ajunge nici la rd.1/rd.3 din D300, nici in D390 — amandoua citesc
        # `facturi`. Numarul vine din SERIA proprie (`emite_factura` numeroteaza), nu din corpul
        # cererii: la o LIVRARE documentul e al nostru, nu al partenerului — spre deosebire de
        # `achizitie_ic`, unde numarul e cel de pe factura furnizorului.
        # Cota e 0: livrarea IC e scutita cu drept de deducere (art. 294 alin. (2) lit. a) pentru
        # bunuri; prestarea IC e neimpozabila in Romania, taxabila la beneficiar (art. 278 alin. (2)).
        # Tara si axa se INGHEATA pe document: tara din chiar codul de TVA al clientului, axa din
        # `tip`, validat mai sus.
        _tara_client, _ = _ic.desparte_cod_tva(corp["cod_tva_client"])
        from core import facturi_api as _fa_vic
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)   # emite_factura foloseste INSERT necalificat
        fres = _fa_vic.emite_factura(
            conn, linii=[{"descriere": descr[:200], "cantitate": 1, "pret_unitar": str(val),
                          "cota_tva": 0}],
            tert_nume=(v.get("nume") or "").strip() or None,
            tert_cui=corp["cod_tva_client"], data_emitere=corp["data"],
            tert_tara=_tara_client, axa_ic=corp.get("tip"))
        fid = fres["factura_id"]
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_facturi_cu_factura(
                cur, schema, corp["data"], fid, descr[:200])[0]
            repo_contabilitate.adauga_linie_client(cur, schema, iid, cont_venit, val)
        conn.commit()
    return {"inregistrare_id": iid, "factura_id": fid, "numar": fres.get("numar"),
            "mentiune": ment, "vies": v}



def intrastat_praguri(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/intrastat-praguri`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import intrastat as _is
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        intro, exped = {}, {}
        with conn.cursor() as cur:
            for directie, cui, luna, baza in repo_facturi.emise_pe_luni_pentru_intrastat(cur, schema, an):
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


def tenant_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants`; docstringul ei a ramas in stratul HTTP."""
    if _uc_comun._TENANT_TEMPLATE is None:
        raise _erori.EsecIntern("template tenant indisponibil pe server")
    # [P5 val 3] ANAF ÎNAINTE de conexiune — vezi nota de la `register`.
    try:
        _d_anaf = tenant_provisioning.date_din_anaf(date.cui)
    except Exception as _e:
        _obs.esec_secundar("precompletare ANAF la firma noua", _e)
        _d_anaf = None
    try:  # tenant_cui_400
        with db.get_conn() as conn:
            r = tenant_provisioning.provision_tenant(
                conn, date.nume, date.cui, ctx["firm"], ctx["uid"], _uc_comun._TENANT_TEMPLATE,
                tip_firma=date.tip_firma)
            # [F188] pre-completare din ANAF v9 - SURSA UNICA (tenant_provisioning.precompleteaza_din_anaf),
            # aceeasi ca la register/import. NU atinge 'nume' (setat de contabil): seteaza_nume=False.
            # ANAF jos -> default, corectabil din Date firma.
            try:
                # [P5 val 3] datele ANAF s-au luat INAINTE de bloc (`_d_anaf`); aici doar scrie.
                tenant_provisioning.precompleteaza_din_anaf(conn, r["schema_name"], _d_anaf, seteaza_nume=False)
            except Exception as _e:
                _obs.esec_secundar("precompletare ANAF la firma noua", _e)  # inghitit, dar nu tacut (27.07.2026)
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    return r


def banca_parse_extras(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/parse-extras`; docstringul ei a ramas in stratul HTTP."""
    _crono.marca("intrare_handler")
    from core import banca_parser, banca as _bk
    _crono.marca("importuri")
    with db.get_conn() as conn:
        _crono.marca("conexiune")
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
    _crono.marca("acces")
    continut = continut
    _crono.marca("citire_fisier")
    try:
        tranzactii = banca_parser.parse_extras(continut, nume_fisier or "")
    except Exception as e:
        raise _erori.CerereGresita(f"nu am putut citi extrasul: {e}")
    _crono.marca("parsare")
    for t in tranzactii:
        linie = {"sens": "debit" if t["suma"] < 0 else "credit",
                 "suma": abs(t["suma"]), "descriere": t.get("detalii", "")}
        r = _bk.regula_cont(linie)
        t["cui"] = r.get("cui")
        t["tip"] = r.get("tip")
        t["nota"] = r.get("nota")
    _crono.marca("reguli")
    return _uc_comun._raspuns({"tranzactii": tranzactii, "nr": len(tranzactii)})



def import_efactura(tenant_id, fisiere, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/import-efactura`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    rezultate = {"importate": 0, "duplicate": 0, "erori": []}
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("tenant inexistent sau fără acces")
        with conn.cursor() as cur:
            rand = repo_firma_profil.cui_firma_3(cur, schema)
            if not rand or not rand[0]:
                raise _erori.DateInvalide(CUI_FIRMA_LIPSA)
            cui_firma = rand[0]
            for continut, nume_fisier in fisiere:
                continut = continut
                try:
                    perechi = _ef.extrage_fisiere(nume_fisier or "f.xml", continut)
                except Exception as e:
                    rezultate["erori"].append(f"{nume_fisier}: {e}")
                    continue
                for nume, xmlb in perechi:
                    try:
                        f = _ef.parseaza_xml(xmlb, cui_firma)
                    except ValueError as e:
                        rezultate["erori"].append(f"{nume}: {e}")
                        continue
                    _fid, _nou = _uc_comun._factura_din_parsat(cur, schema, f)
                    rezultate["importate" if _nou else "duplicate"] += 1
        conn.commit()
    return _uc_comun._raspuns(rezultate)

