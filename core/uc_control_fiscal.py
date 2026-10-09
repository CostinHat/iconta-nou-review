# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/control_fiscal`.

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

from core import db, auth_api
from core import erori as _erori
from core import repo_tenants
from core import uc_comun as _uc_comun
from core.common import azi_ro, pastila_firma
from core import db, auth_api, control_fiscal_api


def control_fiscal_portofoliu(ctx):
    """[P7 · use-case] Corpul rutei `/control-fiscal`; docstringul ei a ramas in stratul HTTP."""
    from core import firma_rezumat as _fr
    out = []
    sumar = {"verde": 0, "galben": 0, "rosu": 0, "gri": 0}
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
        model = _fr.citeste(conn, [f.get("id") for f in firme], ["control_fiscal"])
    for f in firme:
        tid = f.get("id")
        st = (model.get(tid) or {}).get("control_fiscal") or {}
        d = st.get("date") or {}
        curent = st.get("stare") == _fr.CURENT and not d.get("eroare")
        stare = d.get("stare", "gri") if curent else "gri"
        sumar[stare] = sumar.get(stare, 0) + 1
        out.append({"tenant_id": tid, "nume": f.get("nume"), "cui": f.get("cui"),
                    "stare": stare,
                    "lipsa": d.get("lipsa", 0) if curent else 0,
                    "urmarit": d.get("urmarit", 0) if curent else 0,
                    # [eticheta_din_fapt 20.08.2026] fara numarul de neverificabile, lista nu poate
                    # spune DE CE e o firma gri.
                    "neclar": d.get("neclar", 0) if curent else 0,
                    "contabil": d.get("contabil") or [],
                    "prospetime": {"stare": st.get("stare") or _fr.LIPSESTE,
                                   "calculat_la": st.get("calculat_la")}})
    return {"firme": out, "sumar": sumar, "contoare": contoare_portofoliu(out)}


def contoare_portofoliu(firme):
    """[08.10.2026, retest pct.7] Contoarele de sus = FAPTE numărate pe firme, nu culoarea combinată: „F1 și F5 arată «restanță» cu
    «0 restanțe», iar contorul de sus «0 de urmărit», deși detaliul F1 are 5 de urmărit. Nedeclaratul înainte de termen e «de urmărit»,
    nu restanță.” O firmă poate intra în două (restanțe ȘI neconcordanțe); `sumar` (partiția pe culori) rămâne neschimbat.
    [Retest 2, 09.10.2026, pct.3] „contoarele de sus folosesc două reguli … Una dintre reguli, aplicată peste tot.” Regula unică e cea
    a faptelor (de la pct.7): fiecare contor = firmele care AU faptul; „nu se pot verifica” = firma cu cel puțin un necunoscut
    (declarație sau verificare contabilă gri) sau fără date la zi — nu starea principală gri (F5 avea 2 necunoscute și pică din
    numărătoare); „la zi” = firma fără niciun fapt din celelalte patru."""
    neconc = lambda f: any((c or {}).get("stare") in ("rosu", "galben") for c in (f.get("contabil") or []))   # noqa: E731
    gri = lambda f: ((f.get("neclar") or 0) > 0 or any((c or {}).get("stare") == "gri" for c in (f.get("contabil") or []))   # noqa: E731
                     or (f.get("prospetime") or {}).get("stare", "curent") != "curent")
    fapte = {"restante": lambda f: (f.get("lipsa") or 0) > 0, "de_urmarit": lambda f: (f.get("urmarit") or 0) > 0,
             "neconcordante": neconc, "nu_se_pot_verifica": gri}
    out = {k: sum(1 for f in firme if p(f)) for k, p in fapte.items()}
    out["la_zi"] = sum(1 for f in firme if not any(p(f) for p in fapte.values()))
    return out


def control_fiscal_audit_preluare(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/control-fiscal/{tenant_id}/audit-preluare`; docstringul ei a ramas in stratul HTTP."""
    import datetime
    from core import audit_preluare
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = audit_preluare.audit(cs, schema, tenant_id, cp)
        with cp.cursor() as cur:  # creat_la = de cand e firma in iConta sub cabinet (proxy preluare)
            row = repo_tenants.creat_la(cur, tenant_id)
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


def control_fiscal_detaliu(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/control-fiscal/{tenant_id}`; docstringul ei a ramas in stratul HTTP."""
    azi = azi_ro()   # [fus] verdict de zi = zi RO (acelasi ca portofoliul)
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        r = control_fiscal_api.evalueaza_firma(cs, cp, tenant_id, schema, azi)
    try:  # cf_verificari_v1 — ACEEASI functie partajata ca lista: severitatea (pastila_firma) e identica.
        contabil, vc = _uc_comun._construieste_contabil(schema, tenant_id, ctx, azi.year, azi.month, r.get("regim_tva_anaf"))
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



#: tipurile care se pot marca „depusă în afara iConta” — cele nouă pe care le urmărește Control fiscal
TIPURI_DEPUSA_EXTERN = ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406")


#: Sursele unei depuneri MARCATE (nu trimise prin iConta.eu): se pot modifica și anula.
SURSE_MARCATE = ("extern", "contabil_anterior")


def _perioada(corp):
    tip = str(corp.get("tip") or "").strip().lower()
    if tip not in TIPURI_DEPUSA_EXTERN:
        raise _erori.DateInvalide("Tip de declarație necunoscut: %r." % corp.get("tip"))
    try:
        an, luna = int(corp.get("an") or 0), int(corp.get("luna") or 0)
    except (TypeError, ValueError):
        raise _erori.DateInvalide("Perioadă invalidă: %s/%s." % (corp.get("luna"), corp.get("an")))
    if not (2000 <= an <= azi_ro().year and 1 <= luna <= 12):
        raise _erori.DateInvalide("Perioadă invalidă: %s/%s." % (luna, an))
    return tip, an, luna


def control_fiscal_depuse_anterior(tenant_id, corp, ctx):
    """[08.10.2026, retest pct.9, verbatim în DECIZII] „Grupul «Înainte de preluare» […]: pliat implicit, cu o acțiune «Marchează toate
    ca depuse de contabilul anterior».” Marchează perioadele date (numai cele DINAINTEA lunii preluării, fiecare nedepusă) cu sursa
    `contabil_anterior`: depunerea s-a făcut, data ei nu se cunoaște — nu se inventează una, iar clasificarea nu judecă termenul.
    {"marcate": n, "sarite": [{tip, an, luna, motiv}]}."""
    import datetime
    from core import repo_control_fiscal_api, luna_preluare as _lp, repo_firma_profil as _rfp
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    perioade = corp.get("perioade") or []
    if not perioade or len(perioade) > 200:
        raise _erori.DateInvalide("Alege între 1 și 200 de perioade de marcat.")
    with db.get_conn(schema) as cs, cs.cursor() as cur:
        f = _rfp.fapte_preluare(cur)
        preluare = _lp.efectiva(f["salvata"], f["creat_la"], f["data_solduri"], f["prima_nota"])
        cs.rollback()
    from core import afirmatii as _af
    marcate, sarite = 0, []

    def _sarita(tip, an, luna, motiv):   # afirmație tipată (P8), cu cheile pe care le citește ecranul
        return dict(_af.afirmatie("neconformitate", "marcare_depusa_sarita", motiv, unde="%s %02d/%04d" % (tip.upper(), luna, an),
                                  regula="se marchează numai o perioadă dinaintea preluării, încă nedepusă"), tip=tip, an=an, luna=luna)
    acum = datetime.datetime.now(datetime.timezone.utc)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            for p in perioade:
                tip, an, luna = _perioada(p)
                if not preluare or (an, luna) >= tuple(preluare):
                    sarite.append(_sarita(tip, an, luna, "nu e dinaintea preluării"))
                    continue
                if repo_control_fiscal_api.select_depusa_curenta(cur, tenant_id, an, luna, tip):
                    sarite.append(_sarita(tip, an, luna, "e deja înregistrată ca depusă"))
                    continue
                repo_control_fiscal_api.insert_depusa_extern(cur, tenant_id, an, luna, tip, acum, None, sursa="contabil_anterior")
                marcate += 1
        conn.commit()
    return {"ok": True, "marcate": marcate, "sarite": sarite}


def control_fiscal_anuleaza_marcare(tenant_id, corp, ctx):
    """[08.10.2026, retest pct.10] „marcarea nu se poate modifica sau anula” — anularea: cad toate versiunile MARCATE ale perioadei;
    o depunere prin iConta.eu nu se anulează de aici."""
    from core import repo_control_fiscal_api
    _uc_comun._schema_sau_404(ctx, tenant_id)
    tip, an, luna = _perioada(corp)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur_dep = repo_control_fiscal_api.select_depusa_curenta(cur, tenant_id, an, luna, tip)
            if not cur_dep or cur_dep[1] not in SURSE_MARCATE:
                raise _erori.Conflict("%s pe %02d/%d nu e o marcare — nu e nimic de anulat." % (tip.upper(), luna, an))
            n = repo_control_fiscal_api.delete_marcari(cur, tenant_id, an, luna, tip)
        conn.commit()
    return {"ok": True, "anulate": n, "tip": tip, "an": an, "luna": luna}


def control_fiscal_depusa_extern(tenant_id, corp, ctx):
    """[08.10.2026, decizia Costin U2] Marchează o declarație „depusă în afara iConta”, cu recipisa opțională.

    Data depunerii e OBLIGATORIE: fără ea, „la termen / după termen” ar fi o presupunere (data de azi ar face orice declarație
    veche „depusă după termen”). Nu se marchează peste o depunere existentă — aceea e deja „la zi”."""
    import datetime
    from core import repo_control_fiscal_api
    _uc_comun._schema_sau_404(ctx, tenant_id)
    tip, an, luna = _perioada(corp)
    azi = azi_ro()
    try:
        data = datetime.date.fromisoformat(str(corp.get("data_depunere") or "")[:10])
    except ValueError:
        raise _erori.DateInvalide("Scrie data depunerii (de pe recipisă).")
    if data > azi:
        from core.pdf_util import data_ro   # formatorul canonic al datelor pentru ochi (DS cap.4)
        raise _erori.DateInvalide("Data depunerii (%s) e în viitor." % data_ro(data))
    recipisa = (str(corp.get("recipisa") or "").strip() or None)
    if recipisa and len(recipisa) > 100:
        raise _erori.DateInvalide("Numărul recipisei are peste 100 de caractere.")
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur_dep = repo_control_fiscal_api.select_depusa_curenta(cur, tenant_id, an, luna, tip)
            # [retest 08.10 pct.10] o MARCARE se poate modifica (versiune nouă); o depunere prin iConta.eu nu se suprascrie
            if cur_dep and cur_dep[1] not in SURSE_MARCATE:
                raise _erori.Conflict("%s pe %02d/%d e deja depusă prin iConta.eu." % (tip.upper(), luna, an))
            repo_control_fiscal_api.insert_depusa_extern(cur, tenant_id, an, luna, tip, data, recipisa)
        conn.commit()
    return {"ok": True, "tip": tip, "an": an, "luna": luna, "data_depunere": data.isoformat(), "recipisa": recipisa}
