# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/pachete`.

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

from core import db, observare as _obs
import core.pachete_api as _pachete
from core import erori as _erori
from core import uc_comun as _uc_comun


def pachet_rezumat(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/rezumat`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    schema = _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        return _pachete.rezumat_luna(cs, cp, tenant_id, an, luna)


def pachet_genereaza(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/genereaza`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        return _pachete.genereaza_poveste(cs, cp, tenant_id, an, luna, schema)


def pachet_poveste_get(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/poveste`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn() as cp:
        return _pachete.get_poveste(cp, tenant_id, an, luna)


def pachet_poveste_set(tenant_id, an, luna, date, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/poveste`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._pachet_schema(ctx, tenant_id)
    _de_trimis = None           # ce ramane de trimis DUPA ce blocul s-a inchis si a comis
    with db.get_conn() as cp:
        r = _pachete.salveaza_poveste(cp, tenant_id, an, luna, date.text, status=date.status or "ciorna")
        if (date.status or "") == "aprobat":
            email = _uc_comun._email_client_tenant(cp, tenant_id)
            if email:
                nume = _uc_comun._nume_tenant(cp, tenant_id)
                luni_n = ["", "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                          "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]
                subiect = "Raportul lunar - " + (luni_n[luna] if 1 <= luna <= 12 else str(luna)) + " " + str(an)
                html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                        "<p>Buna,</p><p>Contabilul tau a pregatit raportul lunar pentru <b>" +
                        (nume or "firma ta") + "</b>. Il gasesti in portalul iConta.eu, la Povestea lunii.</p>"
                        "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                        "Deschide portalul</a></p></div>")
                _de_trimis = (email, subiect, html)
    # [P5 val 3, 11.09.2026] AICI, dupa bloc. `db.get_conn` comite la IESIREA din el, iar `return r`
    # statea inauntru — deci e-mailul pleca INAINTE ca raportul sa fie sigur salvat. Contract
    # aprobat: commit reusit -> se trimite; commit cazut -> exceptia iese de aici si NU se trimite
    # nimic. In plus, apelul (termen 15 s) nu mai tine o conexiune din pool.
    if _de_trimis is not None:
        _obs.trimite_email_html(*_de_trimis)
    return r


def pachet_preview(tenant_id, an, luna, text, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/preview`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    # preview = ACELASI _html ca trimiterea (corp + semnatura din DB). text vine din editor,
    # deci reflecta ciorna needitata, nu doar ce e salvat in pachet_povestea.
    schema = _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        html = _pachete.preview_html(cs, cp, tenant_id, an, luna, text, ctx.get("uid"), ctx.get("firm"))
    return {"html": html}


def pachet_trimite(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/trimite`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        semnatura = _pachete.semnatura_cabinet(cp, ctx.get("uid"), ctx.get("firm"))
        _pregatit = _pachete.pregateste(cs, cp, tenant_id, an, luna, semnatura=semnatura)
    # [P5 val 3] AICI: cele DOUA conexiuni s-au intors in pool inainte de apelul la Brevo (15 s).
    r = _pachete.trimite_pregatit(_pregatit)
    if not r.get("ok"):
        cod = r.get("cod")
        msg = {"FARA_EMAIL": "Firma nu are email setat in profil.",
               "NEAPROBATA": "Aproba povestea inainte de trimitere.",
               "EMAIL_ESUAT": "Emailul nu a putut fi trimis."}.get(cod, cod or "eroare")
        raise _erori.CerereGresita(msg)
    return r
