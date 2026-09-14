# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/portal`.

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

from core import db, auth_api, facturi_api, portal_api, control_fiscal_api, documente_api
from core import repo_facturi
from core import repo_firma_profil
from core import repo_portal
from core import repo_tenants
from core import repo_utilizatori
from core.mesaje import MESAJ_DOAR_TITULARUL
import core.notificari_api as _notif
import core.pachete_api as _pachete
import psycopg2.extras as _E_audit
import psycopg2.extras as _E_sol
from core import erori as _erori
from core import uc_comun as _uc_comun
from core.mesaje import (EMAIL_INVALID, EMAIL_EXISTA,
                         MESAJ_EMAIL_ACELASI,
                              MESAJ_DOAR_TITULARUL, MESAJ_EMAIL_DE_CONFIRMAT)
from core import db, auth_api, facturi_api, portal_api, control_fiscal_api, observare as _obs, documente_api
import os
from core import nucleu as _nucleu
from core import repo_casa
from core import common as _common
from core import db, auth_api, facturi_api, portal_api, control_fiscal_api, observare as _obs, documente_api


def portal_firme(ctx):
    """[P7 · use-case] Corpul rutei `/portal/firme`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return {"firme": auth_api.tenantii_userului(conn, ctx["uid"])}


def portal_acces_cont(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acces-cont`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _uc_comun._titular_client(cur, t["id"])
            conturi = repo_utilizatori.clientii_firmei(cur, t["id"])
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
            rand = repo_firma_profil.email_firma(cur)
    email_pachet = ((rand[0] if rand else None) or "").strip()
    email_logare = ((principal or {}).get("email") or "").strip()
    return {"principal": principal, "suplimentare": suplimentare,
            "eu_principal": bool(principal) and principal["id"] == ctx["uid"],
            "email_pachet": email_pachet,
            "aceeasi_adresa": bool(email_pachet) and email_pachet.lower() == email_logare.lower()}


def portal_revoca_acces(user_id, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acces-cont/acces/{user_id}`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _uc_comun._titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise _erori.FaraDrept(MESAJ_DOAR_TITULARUL)
            if user_id == pid:
                raise _erori.CerereGresita("nu poți revoca propriul acces principal")
            repo_utilizatori.dezleaga_contul_de_firma(cur, user_id, t["id"])
            if repo_utilizatori.cate_firme_mai_are_contul(cur, user_id)["n"] == 0:
                repo_utilizatori.dezactiveaza_contul(cur, user_id)
            _uc_comun._urma_portal(cur, t["id"], "acces_retras",
                         "clientul a retras accesul utilizatorului #%s" % user_id, ctx["uid"])
    return {"ok": True}


def portal_firma(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/firma`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    return {"tenant_id": t["id"], "nume": t.get("nume"), "firma": firma}


def portal_documente_luni(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/documente/luni`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        luni = documente_api.luni_disponibile(conn, t["schema_name"])
        decl = documente_api.declaratii_depuse(conn, t["id"])
    return {"luni": luni, "declaratii": decl}


def portal_kpi(an, luna, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/kpi`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _d
    from core import kpi_client as _kpi
    t = _uc_comun._tenant_client(ctx, tenant_id)
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, t["schema_name"], an, luna)
    return {"an": an, "luna": luna, "kpi": _kpi.kpi_din_balanta(randuri)}


def portal_cashflow(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/cashflow`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _d
    from core import kpi_client as _kpi
    from core import cashflow as _cf
    t = _uc_comun._tenant_client(ctx, tenant_id)
    azi = _d.today()
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, t["schema_name"], azi.year, azi.month)
    k = _kpi.kpi_din_balanta(randuri)
    with db.get_conn(t["schema_name"]) as conn:
        with conn.cursor() as cur:
            fs = [{"directie": r[0], "data_emitere": str(r[1]),
                   "data_scadenta": str(r[2]) if r[2] else None, "total": float(r[3] or 0)}
                  for r in repo_facturi.pentru_cashflow(cur)]
    emise = _cf.aloca_sold([f for f in fs if f["directie"] == "emisa"], k["de_incasat"])
    primite = _cf.aloca_sold([f for f in fs if f["directie"] == "primita"], k["de_platit"])
    obligatii = _cf.obligatii_din_balanta(randuri)  # portal_cashflow_v2
    medie = _cf.cheltuieli_lunare_cash(randuri, azi.month)
    primite = primite + _cf.plati_estimate(obligatii, medie, azi=azi)
    return {"cash": k["cash"], "medie_cheltuieli": medie,
            "saptamani": _cf.forecast(k["cash"], emise, primite, azi=azi)}


def portal_facturi(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/portal/facturi`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        return {"facturi": facturi_api.lista_facturi(conn, an, luna, None)}


def portal_declaratii(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/declaratii`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        return {"declaratii": portal_api.declaratii_depuse(conn, t["id"])}


def portal_povesti(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/povesti`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
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


def portal_solicitari_contor(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/solicitari/contor`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            n = repo_portal.cate_solicitari_necitite(cur, t["id"])[0]
    return {"necitite": n}


def portal_solicitari_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/solicitari`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_sol.RealDictCursor) as cur:
            rows = repo_portal.solicitarile_firmei(cur, t["id"])
    return {"solicitari": rows}


def portal_solicitari_trimite(date, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/solicitari`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            repo_portal.adauga_solicitare(cur, t["id"], date.mesaj, ctx["uid"])
        with conn.cursor() as cur:
            r = repo_tenants.cabinetul_si_numele(cur, t["id"])
        if r and r[0]:
            with conn.cursor() as cur:
                ids = [x[0] for x in repo_utilizatori.conturi_active_ale_cabinetului(cur, r[0])]
            txt = "Mesaj nou de la %s: %s" % (r[1] or "firma", date.mesaj[:80])
            _notif.adauga_multi(conn, ids, "solicitare_client", txt, link="solicitari:%s" % t["id"])
    return {"ok": True}


def portal_acasa(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acasa`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
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


def portal_schimba_email(date, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acces-cont/email`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, date.tenant_id)
    email_nou = date.email.strip().lower()
    if not _uc_comun._email_valid(email_nou):  # [R138]
        raise _erori.CerereGresita(EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _uc_comun._titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise _erori.FaraDrept(MESAJ_DOAR_TITULARUL)
            _uc_comun._adresa_e_libera(cur, email_nou, ctx["uid"])
            # [R62 (1)] NU se mai scrie `users.email` aici. Adresa e identitatea de autentificare
            # (intrarea se face prin magic-link pe email), deci un UPDATE imediat insemna ca cine
            # are o sesiune deschisa muta contul, definitiv, dintr-un singur camp.
            email_vechi = ((repo_utilizatori.emailul_contului(cur, ctx["uid"]) or {}).get("email") or "").strip().lower()
            if email_vechi == email_nou:
                raise _erori.CerereGresita(MESAJ_EMAIL_ACELASI)
            import secrets as _sec3
            tok = "se_" + _sec3.token_urlsafe(32)
            repo_utilizatori.sterge_schimbarile_de_email_neconfirmate(cur, ctx["uid"])
            repo_utilizatori.cere_schimbarea_de_email(cur, ctx["uid"], t["id"], email_vechi, email_nou, _uc_comun._hash_tok(tok))
            _uc_comun._urma_portal(cur, t["id"], "email_cerut",
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



def portal_adauga_acces(date, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acces-cont/acces`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, date.tenant_id)
    email = date.email.strip().lower()
    if not _uc_comun._email_valid(email):  # [R138]
        raise _erori.CerereGresita(EMAIL_INVALID)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            pid = _uc_comun._titular_client(cur, t["id"])   # [R62 (b)] aceeasi regula ca la citire
            if pid is None or pid != ctx["uid"]:
                raise _erori.FaraDrept(MESAJ_DOAR_TITULARUL)
            firm_id = repo_tenants.cabinetul_firmei(cur, t["id"])["accounting_firm_id"]
            ex = repo_utilizatori.contul_dupa_email_2(cur, email)
            if ex and (ex["rol"] != "client" or ex["activ"]):
                raise _erori.CerereGresita(EMAIL_EXISTA)
            _uc_comun._cere_acelasi_cabinet(ex, firm_id)   # [R62 (2)] izolarea intre cabinete, P12
            import secrets as _sec2
            if ex:
                uid = ex["id"]
                repo_utilizatori.activeaza_contul_cu_nume(cur, date.nume or email.split("@")[0], uid)
                repo_utilizatori.leaga_contul_de_firma_idempotent(cur, uid, t["id"])
            else:
                uid = repo_utilizatori.creeaza_cont(cur, email, _nucleu.hash_parola(_sec2.token_urlsafe(16)), date.nume or email.split("@")[0], firm_id)["id"]
                repo_utilizatori.leaga_contul_de_firma(cur, uid, t["id"])
            tok = "ml_" + _sec2.token_urlsafe(32)
            _uc_comun._pune_token(cur, tok, uid, "48 hours")
            _uc_comun._urma_portal(cur, t["id"], "acces_dat",
                         "clientul a dat acces la portal lui %s (utilizator #%s)" % (email, uid),
                         ctx["uid"])
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#magic=" + tok
    html = ("<p>Buna,</p><p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intra in portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (t.get("nume", ""), link)
    _obs.trimite_email_html(email, "Acces portal iConta.eu — " + t.get("nume", ""), html)
    return {"ok": True}



def portal_bon_confirma(bon_id, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/bon/{bon_id}/confirma`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_pentru_documente(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        if not repo_casa.trece_bonul_la_de_verificat(cur, t['schema_name'], bon_id):
            raise _erori.Inexistent("bon inexistent sau deja trimis")
    return {"ok": True}



def portal_bon_sterge(bon_id, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/bon/{bon_id}`; docstringul ei a ramas in stratul HTTP."""
    import os as _os, shutil as _shutil
    t = _uc_comun._tenant_pentru_documente(ctx, tenant_id)
    with db.get_conn() as conn, conn.cursor() as cur:
        if not repo_casa.sterge_bonul_extras(cur, t['schema_name'], bon_id):
            raise _erori.Inexistent("bon inexistent sau deja trimis")
    dir_bon = _os.path.join(_os.path.expanduser(_uc_comun.BON_DIR_BAZA), t["schema_name"], str(bon_id))
    if _os.path.isdir(dir_bon):
        _shutil.rmtree(dir_bon, ignore_errors=True)
    return {"ok": True}



def portal_documente_balanta(an, luna, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/documente/balanta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        pdf = documente_api.balanta_pdf(conn, t["schema_name"], an, luna, t.get("nume") or "")
    return pdf



def portal_recomanda_preview(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/recomanda/preview`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    nume_firma = (firma or {}).get("nume") or t.get("nume") or ""
    return {"ok": True, "html": _uc_comun._mesaj_recomanda_client_html(nume_firma),
            "subiect": "O recomandare de la " + (nume_firma or "un antreprenor")}



def portal_recomanda(date, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/recomanda`; docstringul ei a ramas in stratul HTTP."""
    emails = [e.strip() for e in (date.emails or []) if e and e.strip()]
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    nume_firma = (firma or {}).get("nume") or t.get("nume") or ""
    html = _uc_comun._mesaj_recomanda_client_html(nume_firma)
    rezultate = _uc_comun._trimite_recomandari(emails, html, "O recomandare de la " + (nume_firma or "un antreprenor"))
    return {"ok": True, "rezultate": rezultate}


def portal_bon(fisiere, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/bon`; docstringul ei a ramas in stratul HTTP."""
    from core import ai_client
    import json as _json, os as _os
    t = _uc_comun._tenant_pentru_documente(ctx, tenant_id)
    if not ai_client.disponibil():
        raise _erori.ServiciuIndisponibil("serviciul AI indisponibil")
    imagini = []
    for continut, nume_fisier in fisiere[:4]:
        b = continut
        if len(b) > 8_000_000:
            raise _erori.CerereGresita("imagine prea mare (max 8MB)")
        # [R155, 05.09.2026] Tipul se citeste din octeti, nu din ce spune browserul: un fisier
        # text numit `.png` soseste cu `content_type: image/png`. Refuzul cade INAINTE de apelul
        # la furnizorul de AI — deci si o cerere platita mai putin pentru un fisier care oricum
        # n-avea ce sa spuna.
        _tip = _common.tip_imagine(b)
        if not _tip:
            raise _erori.DateInvalide("«%s» nu e o imagine: primii octeți nu sunt de JPEG, PNG, "
                                     "GIF sau WEBP. Fotografiază bonul, sau încarcă poza lui."
                                % (nume_fisier or "fișierul trimis"))
        imagini.append((b, _tip))
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
        raise _erori.DateInvalide("nu am putut citi bonul; încearcă o poză mai clară")
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
            for (vechi_id,) in repo_casa.sterge_bonurile_extrase_vechi(cur, schema):
                import shutil as _shutil
                d = _os.path.join(_os.path.expanduser(_uc_comun.BON_DIR_BAZA), schema, str(vechi_id))
                if _os.path.isdir(d):
                    _shutil.rmtree(d, ignore_errors=True)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            tip_doc = "chitanta" if date.get("tip") == "chitanta" else "bon"  # bon_flux_e1b_v1
            bon_id = repo_casa.adauga_bon(cur, schema, date.get("comerciant"), date.get("cui"), date.get("data"), total, tva_11, tva_21, _json.dumps(date.get("articole") or []), _json.dumps(tva_lista), len(imagini), date.get("bon_complet") is not False, tip_doc, date.get("numar_document"), date.get("mentiuni"), int(date.get("orientare") or 0) % 360)[0]
    dir_bon = _os.path.join(_os.path.expanduser(_uc_comun.BON_DIR_BAZA), schema, str(bon_id))
    _os.makedirs(dir_bon, exist_ok=True)
    _EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    for i, (b, mt) in enumerate(imagini, 1):
        with open(_os.path.join(dir_bon, "img_%d.%s" % (i, _EXT.get(mt, "jpg"))), "wb") as fh:
            fh.write(b)
    return {"ok": True, "bon": date, "bon_id": bon_id, "avertismente": avertismente}

