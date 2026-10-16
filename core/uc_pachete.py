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
from core.common import esc as _esc_html   # [C39] text scris de om în HTML-ul emailurilor


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
        date = _pachete.date_poveste(cs, cp, tenant_id, an, luna, schema)
    return _pachete.genereaza_poveste(date, an, luna)   # [R193] modelul, cu conexiunile închise


def pachet_poveste_get(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/poveste`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn() as cp:
        return _pachete.get_poveste(cp, tenant_id, an, luna)


# [comanda Costin 05.10.2026 pct.2] „generarea, editarea și ciorna rămân la «Poate pregăti»; «Aprobă» și «Trimite» cer
# «Poate valida» (textul pleacă la client în numele cabinetului)”. Aprobarea are ruta ei (`/poveste/aproba`, VALIDA): pe aceeași
# rută cu ciorna, garda n-ar fi deosebit-o și interfața n-ar fi putut ascunde doar „Aprobă” (DECIZII 05.10.2026).
MESAJ_APROBARE_PE_RUTA_EI = ("Aprobarea poveștii are acțiunea ei și cere dreptul «Poate valida» — aici se salvează doar "
                             "ciorna.")


COD_POVESTE_ABATERI = "POVESTE_ABATERI"
COD_POVESTE_RESTANTE = "POVESTE_CU_RESTANTE"


def verifica_textul_aprobat(tenant_id, an, luna, date, ctx):
    """[deficiența 288] Verificarea automată de dinaintea aprobării (vezi `pachet_poveste_aproba`): ridică refuzul numit, sau nimic."""
    _uc_comun._cere_perioada(an, luna)
    schema = _uc_comun._pachet_schema(ctx, tenant_id)
    with db.get_conn(schema) as cs, db.get_conn() as cp:
        rz = _pachete.rezumat_luna(cs, cp, tenant_id, an, luna)
    abateri = _pachete.abateri_termeni(_pachete.text_simplu((date.text or "").strip()), rz)
    de_decizie = [a for a in abateri if a.startswith(_pachete.ABATERI_CU_DECIZIE)]
    blocante = [a for a in abateri if a not in de_decizie]
    from core import afirmatii as _af

    def _refuz(cod, abateri, mesaj, regula):
        return dict(_af.afirmatie("neconformitate", "poveste_lunii", mesaj, unde="povestea lunii %02d/%04d" % (luna, an), regula=regula),
                    cod=cod, abateri=abateri, mesaj=mesaj)
    if blocante:
        raise _erori.DateInvalide(_refuz(COD_POVESTE_ABATERI, blocante,
                                         "Povestea nu se aprobă: se abate de la pachet — " + "; ".join(blocante) + ". Corecteaz-o "
                                         "(pachetul spune venituri, cheltuieli și rezultat, ale lunii) și aprob-o din nou.",
                                         "povestea spune cifrele lunii, din pachet (deficiența 288, comanda Costin 16.10.2026)"))
    if de_decizie and not getattr(date, "cu_restante", False):
        raise _erori.DateInvalide(_refuz(COD_POVESTE_RESTANTE, de_decizie,
                                         "Povestea pomenește restanțele / declarațiile cabinetului (" + "; ".join(de_decizie) + "). Ele "
                                         "nu ajung la client fără decizia ta: scoate-le din text, sau confirmă că le trimiți.",
                                         "restanțele cabinetului ajung la client numai cu decizia contabilului (deficiența 288)"))


def pachet_poveste_aproba(tenant_id, an, luna, date, ctx):
    """[comanda Costin 05.10.2026 pct.2] Corpul rutei `/pachete/{tenant_id}/poveste/aproba` („Poate valida”): același
    corp ca ciorna, cu starea `aprobat` (garda de pe rută a decis deja că apelantul poate aproba).
    [deficiența 288, comanda Costin 16.10.2026, verbatim în DECIZII] „Povestea folosește termenii corect (venituri ≠ încasări,
    profit/pierdere) și se verifică automat înainte de aprobare” + „Informațiile despre restanțele cabinetului nu intră în povestea
    trimisă clientului fără decizia expresă a contabilului.” Verificarea de la generare (`abateri_termeni`) rulează acum și pe textul
    APROBAT (editat de om): o abatere de termen, sumă, perioadă sau laudă oprește aprobarea, numită; restanțele / declarațiile trec
    numai cu `cu_restante` — decizia expresă, pe al doilea pas."""
    verifica_textul_aprobat(tenant_id, an, luna, date, ctx)
    return pachet_poveste_set(tenant_id, an, luna, date, ctx, _aprobare=True)


def pachet_poveste_set(tenant_id, an, luna, date, ctx, _aprobare=False):
    """[P7 · use-case] Corpul rutei `/pachete/{tenant_id}/poveste`; docstringul ei a ramas in stratul HTTP."""
    if not _aprobare and (getattr(date, "status", None) or "ciorna") != "ciorna":
        raise _erori.CerereGresita(MESAJ_APROBARE_PE_RUTA_EI)
    status = "aprobat" if _aprobare else "ciorna"
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._pachet_schema(ctx, tenant_id)
    _de_trimis = None           # ce ramane de trimis DUPA ce blocul s-a inchis si a comis
    with db.get_conn() as cp:
        r = _pachete.salveaza_poveste(cp, tenant_id, an, luna, date.text, status=status)
        if status == "aprobat":
            email = _uc_comun._email_client_tenant(cp, tenant_id)
            if email:
                nume = _uc_comun._nume_tenant(cp, tenant_id)
                luni_n = ["", "ianuarie", "februarie", "martie", "aprilie", "mai", "iunie",
                          "iulie", "august", "septembrie", "octombrie", "noiembrie", "decembrie"]
                subiect = "Raportul lunar - " + (luni_n[luna] if 1 <= luna <= 12 else str(luna)) + " " + str(an)
                html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                        "<p>Bună,</p><p>Contabilul tău a pregătit raportul lunar pentru <b>" +
                        _esc_html(nume or "firma ta") + "</b>. Îl găsești în portalul iConta.eu, la Povestea lunii.</p>"
                        "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                        "Deschide portalul</a></p></div>")
                _de_trimis = (email, subiect, html)
    # [P5 val 3, 11.09.2026] AICI, dupa bloc. `db.get_conn` comite la IESIREA din el, iar `return r`
    # statea inauntru — deci e-mailul pleca INAINTE ca raportul sa fie sigur salvat. Contract
    # aprobat: commit reusit -> se trimite; commit cazut -> exceptia iese de aici si NU se trimite
    # nimic. In plus, apelul (termen 15 s) nu mai tine o conexiune din pool.
    if _de_trimis is not None:
        _obs.trimite_email_html_sau_semnaleaza("email pachet lunar", *_de_trimis)
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
               "POVESTE_GOALA": "Povestea lunii e goală — scrie sau generează povestea, apoi aprob-o.",
               "EMAIL_ESUAT": "Emailul nu a putut fi trimis."}.get(cod, cod or "eroare")
        raise _erori.CerereGresita(msg)
    return r
