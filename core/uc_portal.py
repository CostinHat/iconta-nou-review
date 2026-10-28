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
from core.mesaje import (EMAIL_INVALID, MESAJ_EMAIL_ACELASI,
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
                # [B3] doar conturi de CLIENT rămase fără firmă; un angajat/admin/superadmin fără
                # rânduri în `user_tenants` NU se stinge din portal (dezactiveaza_contul_client filtrează pe rol).
                repo_utilizatori.dezactiveaza_contul_client(cur, user_id)
            _uc_comun._urma_portal(cur, t["id"], "acces_retras",
                         "clientul a retras accesul utilizatorului %s" % _uc_comun._cine(cur, user_id), ctx["uid"])
    return {"ok": True}


def portal_firma(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/firma`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        firma = portal_api.date_firma(conn, t["schema_name"])
    return {"tenant_id": t["id"], "nume": t.get("nume"), "firma": firma}


def _preluare(cur):
    """(an, luna) luna preluării efectivă a firmei (cursorul pe schema ei) — `luna_preluare.efectiva`, aceeași regulă ca Date firmă și
    Control fiscal; None când nu se știe."""
    from core import luna_preluare as _lp
    fp = repo_firma_profil.fapte_preluare(cur)
    return _lp.efectiva(fp["salvata"], fp["creat_la"], fp["data_solduri"], fp["prima_nota"])


def _starea_lunilor(conn, schema, luni):
    """[556] Pentru fiecare lună (ISO „AAAA-LL-01”): `definitiva` = luna e închisă de contabil (`perioade_blocate`: nicio notă nu mai
    intră și nu se mai schimbă); altfel provizorie, cu `neverificate` = înregistrările lunii încă nevalidate (ciornele, `ciorne_balanta`)."""
    from core import repo_contabilitate as _rc
    with conn.cursor() as cur:
        inchise = {(int(r[0]), int(r[1])) for r in (tuple(x.values()) if isinstance(x, dict) else x
                                                   for x in _rc.perioade_blocate(cur, schema))}
    out = []
    for iso in luni:
        an, luna = int(iso[:4]), int(iso[5:7])
        definitiva = (an, luna) in inchise
        out.append({"luna": iso, "definitiva": definitiva,
                    "neverificate": 0 if definitiva else documente_api.ciorne_balanta(conn, schema, an, luna)["luna"]})
    return out


def portal_documente_luni(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/documente/luni`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiențele 555 + 556] Lunile balanțelor, fiecare cu starea ei: „Clientul vede doar lunile închise sau cele deschise marcate
    «provizorie»” (pe 22.10 clientul vedea octombrie, cu 42 de ciorne, ca definitivă). Declarațiile nu mai vin și pe aici: cardul
    „Declarații depuse” le are (cardul Documente le arăta a doua oară)."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn() as conn:
        luni = _starea_lunilor(conn, t["schema_name"], documente_api.luni_disponibile(conn, t["schema_name"]))
    return {"luni": luni}


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
        (stare,) = _starea_lunilor(conn, t["schema_name"], ["%04d-%02d-01" % (an, luna)])
    k = _kpi.kpi_din_balanta(randuri)
    with db.get_conn(t["schema_name"]) as conn:
        with conn.cursor() as cur:
            k["facturi_de_incasat"] = _pe_moneda(repo_portal.facturi_deschise_validate(cur, "emisa"), k["de_incasat"])
            k["facturi_de_platit"] = _pe_moneda(repo_portal.facturi_deschise_validate(cur, "primita"), k["de_platit"])
    return {"an": an, "luna": luna, "kpi": k, "luna_definitiva": stare["definitiva"], "neverificate": stare["neverificate"]}


def _pe_moneda(facturi, sold_balanta):
    """[559] „De încasat” / „De plătit” din facturile deschise cu nota validată — aceleași rânduri ca Scadențarul portalului: suma pe
    monedă (lei separat de euro, 468), totalul în lei din evidență (`rest_lei`) și ce arată balanța în plus sau în minus față de facturi
    (sold preluat nedefalcat pe facturi, avans), spus, nu ascuns. Sume ca text zecimal (Decimal), fără float."""
    from decimal import Decimal
    pm = {}
    total_lei = Decimal(0)
    for f in facturi:
        m = (f.get("moneda") or "RON").strip().upper() or "RON"
        pm[m] = pm.get(m, Decimal(0)) + Decimal(str(f.get("rest") or 0))
        total_lei += Decimal(str(f.get("rest_lei") or 0))
    dif = Decimal(str(sold_balanta or 0)) - total_lei
    return {"pe_moneda": [{"moneda": m, "suma": str(pm[m])} for m in sorted(pm, key=lambda m: (m != "RON", m))],
            "nr": len(facturi), "total_lei": str(total_lei), "balanta": str(Decimal(str(sold_balanta or 0))), "fara_factura": str(dif)}


def portal_cashflow(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/cashflow`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _d
    from core import kpi_client as _kpi
    from core import cashflow as _cf
    from core import rulaje_preluate as _rp
    t = _uc_comun._tenant_client(ctx, tenant_id)
    azi = _d.today()
    with db.get_conn() as conn:
        randuri = documente_api.balanta(conn, t["schema_name"], azi.year, azi.month)
    k = _kpi.kpi_din_balanta(randuri)
    with db.get_conn(t["schema_name"]) as conn:
        with conn.cursor() as cur:
            # [lotul 13, 559 + 553] facturile deschise cu nota validată (aceeași bază ca „Cifrele firmei” și Scadențarul), fiecare la
            # scadența ei; ce arată balanța peste ele intră o dată, numit
            emise = _cf.din_facturi(repo_portal.facturi_deschise_validate(cur, "emisa"), k["de_incasat"], _cf.CE_FACTURI_CLIENTI,
                                    _cf.CE_SOLD_INCASAT_FARA_FACTURA, azi)
            primite = _cf.din_facturi(repo_portal.facturi_deschise_validate(cur, "primita"), k["de_platit"], _cf.CE_FACTURI_FURNIZORI,
                                      _cf.CE_SOLD_PLATIT_FARA_FACTURA, azi)
            de_la, luni = _cf.luni_cu_evidenta(azi, _preluare(cur), _rp.are_rulaje(cur, t["schema_name"], azi.year))
    obligatii = _cf.obligatii_din_balanta(randuri)  # portal_cashflow_v2
    medie = _cf.cheltuieli_lunare_cash(randuri, luni)
    primite = primite + _cf.plati_estimate(obligatii, medie, azi=azi)
    return {"cash": k["cash"], "medie_cheltuieli": medie,
            "medie_luni": {"de_la": "%04d-%02d" % (azi.year, de_la), "pana_la": "%04d-%02d" % (azi.year, azi.month), "n": luni},
            "saptamani": _cf.forecast(k["cash"], emise, primite, azi=azi)}


def portal_facturi(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/portal/facturi`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        return {"facturi": facturi_api.lista_facturi(conn, an, luna, None)}


def portal_declaratii(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/declaratii`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:   # [C201] o singură conexiune: `public.declaratii_depuse` și periodicitatea din schema firmei
        return {"declaratii": portal_api.declaratii_depuse(conn, t["id"], conn)}


def portal_povesti(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/povesti`; docstringul ei a ramas in stratul HTTP."""
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:   # [C201] o singură conexiune: poveștile (`public.*`) și cifrele lunii (schema firmei)
        rows = _pachete.lista_povesti_aprobate(conn, t["id"])
        with conn.cursor() as cur:
            preluare = _preluare(cur)
        for r in rows:
            an, luna = r["an"], r["luna"]
            an_p, luna_p = (an - 1, 12) if luna == 1 else (an, luna - 1)
            cur_rz = _pachete.rezumat_luna(conn, conn, t["id"], an, luna)
            r["venituri"] = cur_rz["venituri"]
            r["cheltuieli"] = cur_rz["cheltuieli"]
            r["rezultat"] = cur_rz["rezultat"]
            r["tip"] = cur_rz["tip"]
            # [lotul 13, 558] „Povestea pe septembrie (aprobată înainte de reparația 288) spune tot «încasări de 1.000 de lei» —
            # poveștile trimise cu termeni greșiți se regenerează sau se marchează.” Textul care spune altceva decât cifrele lunii
            # (`pachete_api.abateri_termeni`: termen, sumă, felul rezultatului) sau aprobat pe alte cifre (`depasita`, 314) nu ajunge
            # la client: rândul îl marchează „retras”, cu cifrele lunii; contabilul îl vede depășit și îl reface.
            abateri = [a for a in _pachete.abateri_termeni(r["text"], cur_rz)
                       if not a.startswith(_pachete.ABATERI_CU_DECIZIE)]   # trecute de contabil cu decizie expresă (288c): rămân
            depasita = _pachete.get_poveste(conn, t["id"], an, luna, rz=cur_rz).get("depasita")
            r["retrasa"] = bool(abateri or depasita)
            if r["retrasa"]:
                r["text"] = None
            # [558] „«−13.713 față de luna anterioară» compară cu august, care în iConta nu există; la prima lună nu se face
            # comparație”: luna dinaintea preluării nu are evidență în iConta.eu (`luna_preluare.efectiva`)
            if preluare and (an_p, luna_p) < tuple(preluare):
                r["rezultat_anterior"] = r["diferenta"] = None
            else:
                prev_rz = _pachete.rezumat_luna(conn, conn, t["id"], an_p, luna_p)
                r["rezultat_anterior"] = prev_rz["rezultat"]
                r["diferenta"] = round(cur_rz["rezultat"] - prev_rz["rezultat"], 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
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


#: [lotul 13, deficiența 554] Ce plătește clientul pentru fiecare declarație cu plată, în cuvintele lui, și din ce conturi vine suma: soldul
#: creditor de la sfârșitul perioadei declarate, din balanța notelor validate (`documente_api.balanta`). Termenul de plată e termenul
#: declarației, din sursa unică a termenelor (`control_fiscal_api.evalueaza_firma`, mutat pe zi lucrătoare):
#:   TVA — CF art.326 alin.(1): „Orice persoană trebuie să achite taxa de plată organelor fiscale până la data la care are obligația
#:     depunerii unuia dintre deconturile sau declarațiile prevăzute la art. 323 și 324”;
#:   salarii — CF art.80 alin.(1) (impozitul: „să-l plăti la bugetul de stat până la data de 25 inclusiv a lunii următoare celei pentru care se
#:     plătesc aceste venituri”), art.146 alin.(3) (CAS) și art.168 alin.(3) (CASS): „se plătește [...] până la data de 25 inclusiv a lunii
#:     următoare celei pentru care se plătesc veniturile”, art.220^6 alin.(1) (CAM): „de a o plăti la bugetul de stat [...] până la data de 25
#:     inclusiv a lunii următoare celei pentru care se plătesc veniturile”;
#:   impozitul firmei — CF art.56 alin.(1) (micro): „se efectuează trimestrial, până la data de 25 inclusiv a lunii următoare trimestrului”;
#:     art.41 alin.(1) (profit): „se efectuează trimestrial, până la data de 25 inclusiv a primei luni următoare încheierii trimestrelor I-III”.
#: Declarațiile fără plată (D394, D390, D406…) nu apar: decizia din 05.10.2026 — restanțele declarațiilor rămân alertă la cabinet.
PLATI_DIN_DECLARATII = {
    "d300": ("TVA de plată", ("4423",)),
    "d112": ("Contribuții sociale și impozitul pe salarii", ("431", "436", "444")),
    "d100": ("Impozitul firmei", ("4418", "4411")),
}
#: [554] numele impozitului firmei după regimul ei (Date firmă -> regim fiscal)
IMPOZIT_DUPA_REGIM = {"micro": "Impozitul pe veniturile microîntreprinderii", "profit": "Impozitul pe profit"}


def de_platit(rez, balanta_la, regim, azi):
    """[554] Ce are clientul de plătit și până când: [{ce, perioada, termen, suma (text zecimal) | None, depusa}], din obligațiile
    firmei (`evalueaza_firma`: de urmărit și deja depuse) cu termenul încă neîmplinit. `balanta_la(an, luna)` = rândurile balanței la
    sfârșitul lunii. Suma lipsă (None) = contabilul n-a înregistrat-o încă; zero la o declarație deja depusă = nimic de plătit (rândul nu
    apare). Pur, în afara bazei."""
    from decimal import Decimal
    out = []
    for e, depusa in [(x, False) for x in rez.get("urmarit") or []] + [(x, True) for x in rez.get("confirmate") or []]:
        tip = (e.get("tip") or "").lower()
        if tip not in PLATI_DIN_DECLARATII or not e.get("termen") or str(e["termen"])[:10] < azi.isoformat():
            continue
        ce, conturi = PLATI_DIN_DECLARATII[tip]
        if tip == "d100":
            ce = IMPOZIT_DUPA_REGIM.get((regim or "").strip().lower(), ce)
        suma = sum((Decimal(str(r.get("sf_c") or 0)) for r in balanta_la(e["an"], e["luna"])
                    if any(str(r["cont"]).startswith(c) for c in conturi)), Decimal(0))
        if suma <= 0 and depusa:
            continue
        out.append({"ce": ce, "perioada": e.get("perioada"), "termen": str(e["termen"])[:10],
                    "suma": str(suma) if suma > 0 else None, "depusa": depusa})
    out.sort(key=lambda x: (x["termen"], x["ce"]))
    return out


def portal_acasa(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/acasa`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 554, comanda Costin 13.1] „Clientul vede codurile și termenele de depunere ale cabinetului («d300», «d394», literă
    mică); decizia din 05.10: restanțele declarațiilor rămân alertă la cabinet. Clientul vede ce are de plătit și până când (TVA, impozit,
    contribuții), cu sume, în cuvintele lui.” Panoul nu mai poartă declarațiile (nici restanțele, nici codurile): `de_platit`."""
    from datetime import date as _d
    t = _uc_comun._tenant_client(ctx, tenant_id)
    schema = t["schema_name"]
    azi = _d.today()
    balante = {}
    with db.get_conn(schema) as conn_schema:   # [C201] o singură conexiune (`evalueaza_firma`: conn_public = conn_schema)
        rez = control_fiscal_api.evalueaza_firma(conn_schema, conn_schema, t["id"], schema)

        def balanta_la(an, luna):
            if (an, luna) not in balante:
                balante[(an, luna)] = documente_api.balanta(conn_schema, schema, int(an), int(luna))
            return balante[(an, luna)]
        regim = ((portal_api.date_firma(conn_schema, schema) or {}).get("regim_fiscal"))
        plati = de_platit(rez, balanta_la, regim, azi)
    return {
        "tenant_id": t["id"],
        "nume": t.get("nume"),
        "stare": rez.get("stare"),
        "mesaj": rez.get("mesaj"),
        "de_platit": plati,
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
    # [R73] ALERTA: fara confirmare, adresa nu se muta (cale de acces)
    # [lotul 13, 560 / 268] emailurile de acces la cont sunt tranzacționale: pe Postmark (fără „Dezabonează-te”), cu Brevo rezervă
    _obs.trimite_email_html_sau_semnaleaza("email confirmare adresa noua", email_nou, "Confirmă adresa nouă — iConta.eu",
        "<p>Bună,</p><p>S-a cerut mutarea contului iConta.eu pe adresa asta.</p>"
        "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;"
        "padding:10px 22px;border-radius:6px;text-decoration:none'>Confirmă adresa</a></p>"
        "<p>Linkul e valabil 48 de ore. Dacă nu ai cerut tu, ignoră mesajul — "
        "nu se schimbă nimic.</p>" % link, alerta=True)
    # Adresa VECHE afla, chiar daca nu ea confirma: altfel o mutare de cont ar fi tacuta
    # exact pentru cel care pierde accesul.
    _obs.trimite_email_html_sau_semnaleaza("email anunt adresa veche", email_vechi, "Cerere de schimbare a adresei — iConta.eu",
        "<p>Bună,</p><p>S-a cerut mutarea contului tău iConta.eu pe adresa "
        "<b>%s</b>.</p><p>Dacă nu ai cerut tu, spune-i cabinetului acum: "
        "schimbarea se face doar după confirmarea de pe adresa nouă.</p>" % _common.esc(email_nou))
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
            _uc_comun._refuza_email_ocupat(ex, "client", email, "persoana pe care o inviți", "email")
            _uc_comun._cere_acelasi_cabinet(ex, firm_id)   # [R62 (2)] izolarea intre cabinete, P12
            import secrets as _sec2
            if ex:
                uid = ex["id"]
                repo_utilizatori.activeaza_contul_cu_nume(cur, date.nume or email.split("@")[0], uid)
                repo_utilizatori.leaga_contul_de_firma_idempotent(cur, uid, t["id"])
            else:
                # [lotul 10, C73 / U3] adresa luată între verificare și scriere -> același refuz ca verificarea, nu 500
                from core import chei_unice as _chei
                with _chei.refuza_dublura(cur, _uc_comun.CHEIE_EMAIL, _uc_comun._refuz_email_la_cursa(
                        "client", email, "persoana pe care o inviți", "email")):
                    uid = repo_utilizatori.creeaza_cont(cur, email, _nucleu.hash_parola(_sec2.token_urlsafe(16)),
                                                        date.nume or email.split("@")[0], firm_id)["id"]
                repo_utilizatori.leaga_contul_de_firma(cur, uid, t["id"])
            tok = "ml_" + _sec2.token_urlsafe(32)
            _uc_comun._pune_token(cur, tok, uid, "48 hours")
            _uc_comun._urma_portal(cur, t["id"], "acces_dat",
                         "clientul a dat acces la portal lui %s" % email,
                         ctx["uid"])
    baza = os.environ.get("ICONTA_BAZA_URL", "http://localhost:8010")
    link = baza + "/#magic=" + tok
    html = ("<p>Bună,</p><p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intră în portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (_common.esc(t.get("nume", "")), link)
    # [R73] ALERTA: linkul e singura usa a clientului in portal (ca linkul de logare)
    _obs.trimite_email_html_sau_semnaleaza("email acces portal", email, "Acces portal iConta.eu — " + t.get("nume", ""), html,
                                           alerta=True)
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
    dir_bon = _os.path.join(_common.dir_bonuri(), t["schema_name"], str(bon_id))
    if _os.path.isdir(dir_bon):
        _shutil.rmtree(dir_bon, ignore_errors=True)
    return {"ok": True}



def portal_documente_balanta(an, luna, tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/portal/documente/balanta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:   # [C201] o singură conexiune, pe schema firmei (tabelele publice sunt calificate)
        pdf = documente_api.balanta_pdf(conn, t["schema_name"], an, luna, t.get("nume") or "",
                                        note_client=_note_balanta_client(conn, t["schema_name"], an, luna))
    return pdf


def _note_balanta_client(conn, schema, an, luna):
    """[lotul 13, deficiențele 557 + 556] Rândurile de sub antetul balanței pentru CLIENT, în locul celor pentru contabil: „PDF-ul balanței
    pentru client conține paragraful tehnic adresat contabilului («Importă balanța de la 31.08.2026… Import date › Solduri inițiale»). Pe
    documentul clientului: o notă scurtă («Evidența în iConta.eu începe cu septembrie 2026») sau nimic.” Plus starea lunii: provizorie cât
    timp contabilul n-a închis-o (556)."""
    from core import pachete_api as _pa
    note = []
    (st,) = _starea_lunilor(conn, schema, ["%04d-%02d-01" % (an, luna)])
    if not st["definitiva"]:
        note.append("Provizorie: luna %02d/%d nu e încă închisă de contabil, deci cifrele se pot schimba%s." % (
            luna, an, (" (%s încă neverificate)" % _common.cate(st["neverificate"], "înregistrare", "înregistrări"))
            if st["neverificate"] else ""))
    with conn.cursor() as cur:   # [C201] conexiunea apelantului, pe schema firmei
        preluare = _preluare(cur)
    if preluare and preluare[0] == an and documente_api.avertisment_balanta(conn, schema, an):
        note.append("Evidența în iConta.eu începe cu %s %d." % (_pa.LUNI[preluare[1]], preluare[0]))
    return note



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
        raise _erori.DateInvalide("nu s-a putut citi bonul; încearcă o poză mai clară")
    avertismente = []
    if date.get("bon_complet") is False:
        avertismente.append("Documentul pare incomplet sau greu lizibil \u00een poz\u0103. Fotografiaz\u0103-l \u00eentreg, cu lumin\u0103 bun\u0103 \u0219i totalul vizibil.")  # bon_flux_e3b_v1
    total = float(date.get("total") or 0)  # avertismentul aritmetic se arata doar contabilului (bon_flux_e3b_v1)
    tva_lista = date.get("tva") or []
    # cotele TVA period-aware din common.COTE (Legea 141/2025), nu literali cuplati la anul curent
    _r_std = int(_common.cota("tva_standard", strict=False)[0] * 100)
    _r_red = int(_common.cota("tva_redusa", strict=False)[0] * 100)
    tva_11 = round(sum(float(x.get("valoare") or 0) for x in tva_lista if x.get("cota") == _r_red), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tva_21 = round(sum(float(x.get("valoare") or 0) for x in tva_lista if x.get("cota") == _r_std), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    schema = t["schema_name"]
    with db.get_conn() as conn:  # verif_doc_pozate_v1: drafturi abandonate >24h se curata (rand + poze)
        with conn.cursor() as cur:
            vechi = [v for (v,) in repo_casa.sterge_bonurile_extrase_vechi(cur, schema)]
    import shutil as _shutil
    for vechi_id in vechi:   # [R193] pozele se șterg după ce conexiunea s-a întors în pool, nu cu ea în mână
        d = _os.path.join(_common.dir_bonuri(), schema, str(vechi_id))
        if _os.path.isdir(d):
            _shutil.rmtree(d, ignore_errors=True)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            tip_doc = "chitanta" if date.get("tip") == "chitanta" else "bon"  # bon_flux_e1b_v1
            bon_id = repo_casa.adauga_bon(cur, schema, date.get("comerciant"), date.get("cui"), date.get("data"), total, tva_11, tva_21, _json.dumps(date.get("articole") or []), _json.dumps(tva_lista), len(imagini), date.get("bon_complet") is not False, tip_doc, date.get("numar_document"), date.get("mentiuni"), int(date.get("orientare") or 0) % 360)[0]
    dir_bon = _os.path.join(_common.dir_bonuri(), schema, str(bon_id))
    _os.makedirs(dir_bon, exist_ok=True)
    _EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    for i, (b, mt) in enumerate(imagini, 1):
        with open(_os.path.join(dir_bon, "img_%d.%s" % (i, _EXT.get(mt, "jpg"))), "wb") as fh:
            fh.write(b)
    return {"ok": True, "bon": date, "bon_id": bon_id, "avertismente": avertismente}



def scadentar_client(tenant_id, ctx):
    """[lotul 13, deficiența 559, comanda Costin 13.1] Scadențarul pe care îl vede CLIENTUL (`/tenants/{id}/scadentar` cu rolul client):
    „Cifrele firmei arată «De încasat 3.500» (= sold 4111 din note validate), scadențarul însumează ~10.900 lei + 12,10 EUR (include
    facturi cu note nevalidate). [...] Portalul folosește aceeași bază peste tot.” Aceleași facturi ca „De încasat” din „Cifrele firmei”
    (`repo_portal.facturi_deschise_validate`), clasificate de aceeași funcție ca la cabinet (`scadentar.scadentar`); clientul nu umblă la
    notificările de plată (`optin` = False, butoanele lor nu apar)."""
    from datetime import date as _d
    from core import scadentar as _sc
    t = _uc_comun._tenant_client(ctx, tenant_id)
    with db.get_conn(t["schema_name"]) as conn:
        with conn.cursor() as cur:
            facturi = [dict(f, suma=f["rest"]) for f in repo_portal.facturi_deschise_validate(cur, "emisa")]
    rez = _sc.scadentar(facturi, _d.today())
    rez["optin"] = False
    return rez
