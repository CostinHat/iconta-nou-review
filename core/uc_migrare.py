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
from core import afirmatii as _afirmatii
from core.unde import Unde as _Unde
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
        raise _erori.EsecIntern("Șablonul pentru o firmă nouă lipsește pe server — anunță administratorul platformei.")
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
            # [459, comanda Costin 11.3 pct.5] CUI-ul care nu e valabil (cifra de control, numai cifre) se respinge pe rândul lui, cu
            # motivul, înainte de provizionare (până azi `provision_tenant` ridica, iar `except Exception` de mai jos îl spunea „eroare internă”)
            _m_cui = tenant_provisioning.motiv_cui_firma_invalid(f.cui)
            if _m_cui:
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume, f.cui), "cui_invalid", _m_cui, cui=str(f.cui), nume=nume))
                continue
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
                # [comanda Costin 8.2 pct.4: „erorile interne nu ajung la utilizator”] textul excepției merge în jurnal
                _obs.esec_secundar("crearea firmei la importul din migrare", e)
                erori.append(migrare_api.respinge(
                    "firmă", "firma %s (CUI %s)" % (nume, f.cui), "creare_esuata",
                    "nu s-a putut crea (eroare internă, consemnată în jurnalul aplicației) — reîncearcă; dacă se repetă, scrie-ne",
                    cui=str(f.cui), nume=nume))
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


def cui_de_trimis(curatate, din_fisier=False):
    """[342 + 393] (invalide, de_intrebat) pentru codurile curățate (`anaf_api.separa_cui`): cifra de control se verifică ÎNAINTE de ANAF
    (`identitate.valideaza_cui`); un CUI greșit e numit („cifra de control greșită”, cu locul unde se corectează: „în fișier” / „în lista
    lipită”) și nu se trimite."""
    from core import identitate
    invalide, de_intrebat = [], []
    for c in curatate:
        ok, motiv = identitate.valideaza_cui(c)
        if ok:
            de_intrebat.append(c)
        else:
            # [342, comanda Costin 8.2] CUI-ul cu cifra de control greșită nu se trimite la ANAF („negăsit” ar fi fals): se spune ce e greșit
            invalide.append(_afirmatii.afirmatie(
                "fapt", "cod fiscal invalid", "CUI %s: %s — corectează-l %s" % (
                    c, "cifra de control greșită" if motiv == "cifra de control" else motiv, "în fișier" if din_fisier else "în lista lipită"),
                unde=_Unde("firma", str(c)), temei_completitudine="algoritmul cifrei de control a codului fiscal, pe codul %s" % (
                    "citit din fișier" if din_fisier else "lipit"),
                cui=str(c), denumire="", gasit=False, cui_invalid=True))
    return invalide, de_intrebat


def rezultate_validare(rez, curatate, ignorate, invalide, ctx):
    """[341] Răspunsul ANAF + codurile greșite, în ordinea listei; o firmă deja în portofoliu se marchează (`deja_in_portofoliu`)."""
    from core import auth_api, db
    with db.get_conn() as conn:
        portofoliu = {"".join(ch for ch in str(f.get("cui") or "") if ch.isdigit()): f.get("nume")
                      for f in auth_api.tenantii_userului(conn, ctx["uid"])}
    for r in rez:
        nume = portofoliu.get("".join(ch for ch in str(r.get("cui") or "") if ch.isdigit()))
        r["deja_in_portofoliu"] = nume is not None
        if nume is not None:
            r["nume_in_portofoliu"] = nume
    ordine = {str(c): i for i, c in enumerate(curatate)}
    return {"rezultate": sorted(rez + invalide, key=lambda r: ordine.get(str(r.get("cui")), 10 ** 6)), "ignorate": ignorate}


def migrare_valideaza(cui_uri, ctx, din_fisier=False):
    """[P7 · use-case] `POST /migrare/valideaza` — CUI-urile firmelor de importat, verificate la ANAF.
    [deficiența 342, comanda Costin 8.2] cifra de control se verifică ÎNAINTE de ANAF (`identitate.valideaza_cui`, ca la Parteneri): un CUI
    greșit e numit „cifra de control greșită”, nu „nu a fost găsit la ANAF”, și nu se mai trimite; [341] o firmă deja în portofoliu se
    marchează (`deja_in_portofoliu`, cu numele ei de acolo) — nu se mai bifează și nu se mai oferă la import.
    [393, lotul 9] Același drum pentru CUI-urile lipite și pentru cele din fișier (`/migrare/incarca` le trecea direct la ANAF, fără
    cifra de control și fără portofoliu): `cui_de_trimis` + `rezultate_validare`; remediul spune unde e codul."""
    from core import anaf_api
    if not cui_uri:
        return {"rezultate": [], "ignorate": []}
    curatate, ignorate = anaf_api.separa_cui(cui_uri)
    invalide, de_intrebat = cui_de_trimis(curatate, din_fisier)
    try:
        rez = anaf_api.valideaza_cui(de_intrebat) if de_intrebat else []
    except Exception as e:
        raise _erori.ServiciuStrainCazut(anaf_api.mesaj_indisponibil(e))   # [303 + 317]
    return rezultate_validare(rez, curatate, ignorate, invalide, ctx)


#: [371, retestul 19.10.2026: „Rețete (HoReCa) oferă toate firmele, inclusiv PFA și FISCALOS ICONTA. Import RIP e filtrat corect.”] straturile
#: care, pe lângă regim, cer ca firma să fie HoReCa — regula existentă a ecranului Stocuri (`stocuri_cv_api.retete_vizibile`: CAEN-ul în
#: lista din CF, sau firma are deja rețete), nu una nouă
STRATURI_HORECA = ("retete",)


def _strat_aplicabil(strat, firma):
    """Stratul se aplică firmei (`{tip_firma, schema_name}`): regimul (`migrare_api.straturi_pentru`) și, la Rețete, HoReCa."""
    if strat not in migrare_api.straturi_pentru(firma.get("tip_firma")):
        return False
    if strat in STRATURI_HORECA:
        from core import stocuri_cv_api
        sch = firma.get("schema_name")
        if not sch:
            return False
        with db.get_conn(sch) as c:
            return stocuri_cv_api.retete_vizibile(c, sch)
    return True


def migrare_firme_strat(strat, ctx):
    """[P7 · use-case] Corpul rutei `GET /migrare/firme` — [deficiența 371, comanda Costin 8.2] firmele portofoliului
    cărora li se aplică stratul (`migrare_api.straturi_pentru`, după regimul fiecărei firme; [371, lotul 9] Rețete numai la HoReCa)."""
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
    return {"strat": strat, "firme": [{"tenant_id": f.get("id"), "nume": f.get("nume"), "cui": f.get("cui"), "tip_firma": f.get("tip_firma")}
                                      for f in firme if _strat_aplicabil(strat, f)]}


def straturi_firmei(tenant_id, ctx):
    """[371, lotul 9] Straturile aplicabile UNEI firme (meniul ei de import): aceeași regulă ca lista din Migrare cabinet."""
    with db.get_conn() as conn:
        firme = [f for f in auth_api.tenantii_userului(conn, ctx["uid"]) if f.get("id") == int(tenant_id)]
    if not firme:
        raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    return {"straturi": [s for s in migrare_api.straturi_pentru(firme[0].get("tip_firma")) if _strat_aplicabil(s, firme[0])]}


def terti_in_balanta_firme(firme):
    """[P7 · use-case] Pentru `GET /migrare/parteneri` — [deficiența 345, comanda Costin 8.2] stratul nu se marchează terminat cât
    o firmă are în balanța de deschidere solduri pe conturi de terți (4111 / 401 / 409 / 419) fără solduri pe parteneri; se citește numai
    pentru firmele fără parteneri. `firme` poartă `_schema`, care se scoate aici."""
    from core import solduri_parteneri_api
    for x in firme:
        sch = x.pop("_schema")
        x["terti_in_balanta"] = []
        if not x["are_parteneri"] and sch:
            # [lotul 10] firma ștearsă între timp: rămâne fără terți (ca firma fără schemă), nu 500
            x["terti_in_balanta"] = db.pe_firma_existenta(sch, solduri_parteneri_api.terti_in_balanta)[1] or []
    return firme
