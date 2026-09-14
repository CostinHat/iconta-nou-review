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
    return {"firme": out, "sumar": sumar}


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

