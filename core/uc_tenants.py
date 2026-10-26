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

from decimal import Decimal, ROUND_HALF_UP
from core import afirmatii as _af
from core import common as _common
from core import cont_valid as _cv
from core import db, auth_api, tenant_provisioning, facturi_api, clienti_api, salariati_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, vector_fiscal_api, firma_profil_api as _fp, observare as _obs, documente_api
from core import articole_import_api, retete_import_api
from core import cote_tva
from core import repo_banca
from core import repo_casa
from core import repo_contabilitate
from core import jurnal_api as _jurnal_api
from core import repo_declaratii
from core import repo_efactura
from core import repo_facturi
from core import repo_firma_profil
from core import repo_mijloace_fixe
from core import repo_operatiuni
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
from core.mesaje import COD_SERIE_CHITANTA_LIPSA, MESAJ_SERIE_CHITANTA_LIPSA   # [decizii 07.10 pct.5]
from core.pdf_util import bani, data_ro
from core.salariat_decont import cif_partener as _cif_partener   # [lotul 13] punctul unic al CNP-ului pe rând (și Casa îl folosește)
from core.unde import Unde as _Unde
import os
import psycopg2.extras as _E_audit
import psycopg2.extras as _E_sol
from core import erori as _erori
from core import chei_unice as _chei   # [lotul 10, C73] refuzul numit al cheii naturale dublate
from core import uc_comun as _uc_comun
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core.mesaje import (EMAIL_INVALID, CUI_FIRMA_LIPSA,
                         MESAJ_Z_FARA_CHEIE, MESAJ_Z_FARA_BONURI, MESAJ_AMEF_FARA_BONURI, MESAJ_FACTURA_BON_STOC,
                              FARA_DREPT_VALIDARE)
from core import nucleu as _nucleu, articole_import_api, retete_import_api, rip_migrare_api
import psycopg2 as _psycopg2
from core.mesaje import (EMAIL_INVALID, CUI_FIRMA_LIPSA,
                         MESAJ_Z_FARA_CHEIE,
                              FARA_DREPT_VALIDARE)
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core import cronometru as _crono
from core import db, auth_api, tenant_provisioning, facturi_api, migrare_api, solduri_api, solduri_parteneri_api, salariati_import_api, asociati_import_api, mijloace_fixe_import_api, istoric_declaratii_import_api, produse_api, firma_profil_api as _fp, factura_pdf as _pdf, observare as _obs, documente_api
from core.mesaje import (EMAIL_INVALID, CUI_FIRMA_LIPSA,
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return tenant_stergere.previzualizare(conn, tenant_id)


def tenant_nume_ales(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nume-ales`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            return tenant_provisioning.alege_denumirea(conn, tenant_id, date.alege, ctx["uid"])
        except ValueError as e:
            raise _erori.CerereGresita(str(e))


def tenant_scoate(tenant_id, confirmare, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    return d


def client_acces_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/client-acces`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            return {"clienti": repo_utilizatori.conturi_client_ale_firmei(cur, tenant_id)}


def client_acces_revoca(tenant_id, user_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/client-acces/{user_id}`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            repo_utilizatori.dezactiveaza_clientul_firmei(cur, user_id, tenant_id)
            _uc_comun._urma_portal(cur, tenant_id, "acces_retras",
                         "cabinetul a retras accesul utilizatorului %s" % _uc_comun._cine(cur, user_id), ctx["uid"])
    return {"ok": True}


def acces_portal_preview(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/acces-portal`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            tot = repo_contabilitate.toate_conturile(cur)   # planul întreg: lista fără căutare și analiticele fiecărui cont
            if q and q.strip()[:1].isdigit():
                # [deficiența 219, retestul Costin 09.10: „căutarea «73» găsește și 473; căutarea după simbol potrivește începutul”]
                rows = repo_contabilitate.conturi_dupa_inceputul_simbolului(cur, q.strip())
            elif q:
                rows = repo_contabilitate.conturi_dupa_text(cur, f"%{q}%", f"%{q}%")
            else:
                rows = tot
            from core import plan_legal as _pl   # [08.10, V3] contul din afara planului legal se vede ca atare
            afara = set(_pl.in_afara(cur, schema, [r[0] for r in rows]))
            folosite = repo_contabilitate.conturi_folosite(cur, [r[0] for r in rows])   # [Retest 2 pct.13]
            cu_sold = repo_contabilitate.conturi_cu_sold_initial(cur, [r[0] for r in rows])   # [deficiența 218]
    toate = [x[0] for x in tot]
    # [deficiența 369, comanda Costin 8.2] funcțiunea vine din planul OMFP (`plan_functiune`, generat din OMFP 1802/2014 pct.594; analiticul
    # o moștenește de la sintetic), nu din coloana `tip` — scrisă „Bifunctional” pe toate conturile la crearea firmei
    from core import plan_functiune as _pf
    return {"conturi": [{"simbol": r[0], "denumire": r[1], "functiune": _pf.functiune(r[0]),
                         "tip": _pf.ETICHETA.get(_pf.functiune(r[0]), "funcțiune necunoscută (cont din afara planului general)"),
                         "in_afara_planului": r[0] in afara,
                         "sintetic": sintetic_al(r[0]), "folosit": r[0] in folosite,
                         "nu_se_sterge": motiv_nestergere(r[0], folosite, cu_sold, afara, toate)} for r in rows]}


def motiv_nestergere(simbol, folosite, cu_sold, afara, toate):
    """[Retest 2 pct.13, decizia Costin O12: „un cont folosit în note nu se poate șterge”; deficiența 218, retestul Costin 09.10.2026:
    „Sinteticele legale nu se șterg; niciun cont cu sold sau rulaj nu se șterge.”] De ce contul NU se șterge din plan, sau None.
    O SINGURĂ regulă, pentru listă (ecranul nu oferă „Șterge”) și pentru ștergere (serverul refuză)."""
    if simbol in folosite:
        return "apare în note contabile (are rulaj), deci evidența îl folosește"
    if simbol in cu_sold:
        return "are sold inițial (de preluare)"
    if sintetic_al(simbol) is None and simbol not in afara:
        return "e cont sintetic din planul de conturi general — sinteticele legale nu se șterg"
    copii = [c for c in toate if sintetic_al(c) == simbol]
    if copii:
        return "are analitice în plan (%s); șterge-le întâi pe ele" % ", ".join(copii[:10])
    return None


#: [Retest 2 pct.13] separatorii analiticului — aceiași pe care îi acceptă adăugarea (`tenant_plan_conturi_adauga`)
SEPARATORI_ANALITIC = "._-/"


def sintetic_al(simbol):
    """„4111.01” -> „4111”; un cont fără separator e sintetic (None). Analiticul se scrie după sintetic (adăugarea o cere)."""
    s = str(simbol or "")
    poz = [s.index(c) for c in SEPARATORI_ANALITIC if c in s]
    return s[:min(poz)] if poz else None


def tenant_plan_conturi_sterge(tenant_id, simbol, ctx):
    """[Retest 2 pct.13, decizia Costin O12] „un cont folosit în note nu se poate șterge”. Un sintetic cu analitice în plan nu se
    șterge nici el (analiticele ar rămâne fără cont-părinte) — refuzul le numește."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    simbol = (simbol or "").strip()
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            den = repo_contabilitate.denumirea_contului(cur, simbol)
            if not den:
                raise _erori.Inexistent("Contul %s nu e în planul firmei." % simbol)
            from core import plan_legal as _pl
            motiv = motiv_nestergere(simbol, repo_contabilitate.conturi_folosite(cur, [simbol]),
                                     repo_contabilitate.conturi_cu_sold_initial(cur, [simbol]), set(_pl.in_afara(cur, schema, [simbol])),
                                     [r[0] for r in repo_contabilitate.toate_conturile(cur)])
            if motiv:
                raise _erori.Conflict("Contul %s („%s”) nu se poate șterge: %s." % (simbol, den[0], motiv))
            repo_contabilitate.sterge_cont_din_plan(cur, simbol)
        conn.commit()
    return {"ok": True, "simbol": simbol}


def tenant_plan_conturi_adauga(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/plan-conturi`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    simbol = (date.simbol or "").strip()
    denumire = (date.denumire or "").strip()
    # [lotul 11, deficiența 440] simbolul și denumirea se verifică amândouă, fiecare lângă câmpul ei din Plan de conturi (`pc-…`,
    # migrare.js); regulile simbolului sunt trepte ale aceleiași greșeli — se spune prima care cade, plus lungimea
    er = _erori.ErorileFormularului("Contul nu s-a adăugat")
    if not simbol:
        er.camp("pc-simbol", "Completează simbolul contului.")
    # [lotul 3, 04.09.2026] `simbol="ABC"` intra in plan si de acolo putea ajunge pe o nota, intr-o
    # balanta si intr-o declaratie. Criteriul e DERIVAT din nomenclatorul propriu: planul general
    # seed-uit la crearea firmei are peste 700 de conturi, toate incepand cu o cifra de clasa.
    elif not simbol[0].isdigit() or simbol[0] == "0":
        er.camp("pc-simbol", "Simbolul contului începe cu cifra clasei (1-9), ca toate "
                             "conturile din planul general — s-a primit %r. Dacă e un analitic, "
                             "scrie-l după contul sintetic (de exemplu 4111.01)." % simbol)
    elif not all(c.isdigit() or c in "._-/" for c in simbol):
        er.camp("pc-simbol", "Simbolul contului se scrie din cifre, cu separator pentru "
                             "analitic (punct, linie jos, cratimă sau bară) — s-a primit %r." % simbol)
    # [Retest 2 pct.13, prins la proba din ecran] „4111.” trecea: un separator fără analitic după el, sau doi separatori la rând,
    # nu numesc niciun cont. Analiticul = sinteticul + separator + cifre (4111.01), oricâte niveluri.
    else:
        import re as _re
        if not _re.fullmatch(r"[1-9]\d*(?:[._/-]\d+)*", simbol):
            er.camp("pc-simbol", "Analiticul se scrie după contul sintetic, cu cifre după separator (de exemplu 4111.01) — s-a "
                                 "primit %r." % simbol)
    if len(simbol) > 10:
        er.camp("pc-simbol", "Simbolul contului are cel mult 10 caractere — s-a primit %r (%d)." % (simbol, len(simbol)))
    if not denumire:
        er.camp("pc-denumire", "Completează denumirea contului.")
    er.refuza()
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            # Regula 4 + 14.4: un simbol care exista deja NU se suprascrie tacut (ar redenumi un cont OMFP
            # standard, seed-uit la crearea firmei). Calea bulk (solduri_api) foloseste ON CONFLICT DO NOTHING;
            # calea manuala refuza explicit, cu denumirea contului existent, si trimite la cautarea de mai sus.
            def _cont_existent(cur, _e=None):   # [lotul 10, C73 / U2] o singură verificare: înaintea scrierii și la cursă
                existent = repo_contabilitate.denumirea_contului(cur, simbol)
                if existent:
                    raise _erori.Conflict("Contul %s există deja în plan: „%s”. Caută-l în lista de mai sus; dacă ai nevoie "
                            "de un cont diferit, folosește alt simbol." % (simbol, existent[0]))
            # [lotul 13, deficiența 589] „Adăugarea manuală doar pentru analitice sub sintetic legal” — refuzul înaintea oricărei scrieri,
            # lângă câmpul simbolului; aceeași regulă o spune ecranul înainte de „Adaugă” (`plan_legal.refuz_adaugare_manuala`)
            from core import plan_legal as _pl589
            _refuz589 = _pl589.refuz_adaugare_manuala(cur, schema, simbol, sintetic_al(simbol),
                                                      [r[0] for r in repo_contabilitate.toate_conturile(cur)])
            if _refuz589:
                _erori.ErorileFormularului("Contul nu s-a adăugat").camp("pc-simbol", _refuz589).refuza()
            _cont_existent(cur)
            # [369] funcțiunea nu se alege: contul o moștenește de la sinteticul lui din planul OMFP (`plan_functiune`)
            from core import plan_functiune as _pf
            # [lotul 10, C73 / U2] două adăugări simultane ale aceluiași simbol treceau amândouă de verificarea de mai sus, iar a doua
            # cădea cu 500 pe cheia primară `plan_conturi_pkey`: acum ACELAȘI 409, cu contul scris între timp
            with _chei.refuza_dublura(cur, ("plan_conturi_pkey",), _cont_existent):
                repo_contabilitate.adauga_cont_in_plan(cur, simbol, denumire, _pf.ETICHETA.get(_pf.functiune(simbol), "Nedeterminat"))
            from core import plan_legal as _pl   # [08.10, V3] „nu se poate crea … fără avertisment”
            av = _pl.avertisment(cur, schema, [simbol])
        conn.commit()
    return {"ok": True, "simbol": simbol, "avertisment": av}


def solduri_rezumat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solduri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_api.rezumat(conn)


def solduri_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/solduri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [lotul 10, 425] soldul la 1 ianuarie și rulajele anului, când balanța le are (`solduri_api.verifica_rulaje` le verifică la scriere)
    randuri = [{"cont": r.cont, "denumire": r.denumire, "debit": r.debit, "credit": r.credit, "rand_fisier": r.rand_fisier,
                **{k: getattr(r, k, None) for k in solduri_api.CHEI_RULAJE}}
               for r in date.randuri]
    with db.get_conn(schema) as conn:
        # [deficiența 343, comanda Costin 8.2] un cont din afara planului legal al normei firmei nu intră (și nu se mai adaugă tacit în plan)
        from core import plan_legal as _pl
        from core import metoda_stoc as _ms
        with conn.cursor() as cur:
            afara = _pl.in_afara(cur, schema, [r["cont"] for r in randuri])
            # [425] „când balanța are sold pe 371, metoda de stoc se cere la migrare, nu rămâne «nedeclarată»”: fără alegere -> refuz numit,
            # ÎNAINTE de orice scriere
            cere_metoda = solduri_api.are_sold_marfa(randuri) and _ms.citeste(cur, schema) is None
        # [440] conturile din afara planului și metoda de stoc lipsă se spun deodată (`ErorileFormularului`), nu una după alta
        _er = _erori.ErorileFormularului("Balanța nu s-a salvat")
        if afara:
            _er.fara_camp(MESAJ_CONT_IN_AFARA % ", ".join(afara))
        if cere_metoda and not (date.metoda_stoc or "").strip():
            _er.camp("metoda_stoc", MESAJ_METODA_STOC)
        _er.refuza()
        try:
            rez = solduri_api.importa(conn, randuri, date.data_referinta, inlocuieste=bool(date.inlocuieste))
            if cere_metoda:
                with conn.cursor() as cur:
                    rez["metoda_stoc"] = _ms.declara_la_migrare(cur, schema, date.metoda_stoc, ctx["uid"])
            return rez
        except migrare_api.InlocuireNeconfirmata as e:   # [426] înlocuirea cere confirmare -> 409 cu totalurile vechi și noi
            raise _erori.Conflict(str(e))
        except ValueError as e:  # balanta neechilibrata -> 422 cu mesaj explicativ
            raise _erori.DateInvalide(str(e))


#: [lotul 10, 425] refuzul salvării unei balanțe cu sold pe mărfuri la o firmă fără metoda de stoc declarată
MESAJ_METODA_STOC = ("Balanța are sold pe mărfuri (371): alege metoda de stoc a firmei — global-valoric (preț cu amănuntul) sau "
                     "cantitativ-valoric (fișe de magazie, CMP). De ea depinde cum se descarcă marfa; fără ea nu se emite nicio factură cu "
                     "marfă.")


#: [343] refuzul contului care nu e în planul legal al normei firmei (OMFP 1802/2014 pct.594 la societăți)
MESAJ_CONT_IN_AFARA = ("Contul %s nu există în planul de conturi al normei firmei, deci balanța nu se poate prelua așa: corectează contul în "
                       "fișier (un analitic se scrie sub sinteticul lui, de exemplu 401.00012) și încarcă din nou.")


def solduri_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Previzualizarea balanței de deschidere (`POST /tenants/{tenant_id}/solduri/incarca`), fără salvare.
    [343] conturile din afara planului legal al normei se arată respinse, cu motivul; [344] data balanței se propune: ultima zi a lunii
    dinaintea preluării (`bilant_api.data_soldurilor`, aceeași regulă ca luna preluării din Date firmă)."""
    from core import plan_legal as _pl
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        det = solduri_api.extrage_balanta_detaliat(continut, nume_fisier)
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    randuri = det["randuri"]
    from core import metoda_stoc as _ms
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            afara = set(_pl.in_afara(cur, schema, [r["cont"] for r in randuri]))
            # [425] metoda de stoc se cere aici când balanța are sold pe 371 și firma n-o are declarată
            cere_metoda = solduri_api.are_sold_marfa(randuri) and _ms.citeste(cur, schema) is None
        data_propusa = _data_soldurilor(conn, schema)
        # [426] „înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi […]; dacă există note pe lunile de
        # după preluare, spune că soldurile lor se recalculează”
        existenta = solduri_api.rezumat(conn)
        with conn.cursor() as cur:
            note = solduri_api.note_dupa(cur, data_propusa)
    from core.audit_preluare import parte_gresita as _parte_gresita
    for r in randuri:
        r["stare"] = "respins" if r["cont"] in afara else "ok"
        r["motive"] = ["contul %s nu există în planul de conturi al normei firmei" % r["cont"]] if r["cont"] in afara else []
        # [392, retestul 19.10.2026: „5121 cu sold creditor intră fără avertisment la import (auditul de preluare îl prinde)”] aceeași regulă
        # ca auditul (`audit_preluare.parte_gresita`), spusă pe rând, înainte de salvare; rândul intră, cu observația
        _g = None if r["cont"] in afara else _parte_gresita(r["cont"], r.get("debit"), r.get("credit"))
        if _g:
            r["stare"] = "semnalat"
            r["motive"] = ["%s: soldul stă pe partea opusă funcțiunii contului (OMFP 1802/2014 pct.593 alin.(2)) — verifică sensul în balanța "
                           "primită" % _g]
    from decimal import Decimal as _D
    td = float(sum((_D(str(r["debit"] or 0)) for r in randuri), _D(0)))
    tc = float(sum((_D(str(r["credit"] or 0)) for r in randuri), _D(0)))
    valida, motiv = solduri_api.balanta_valida(randuri)
    baza = {"randuri": randuri, "total_debit": td, "total_credit": tc, "valida": valida and not afara,
            "coloane": det["coloane"], "ignorate": det["ignorate"], "sintetice_inlocuite": det["sintetice_inlocuite"],
            "fara_sold": det["fara_sold"], "data_propusa": data_propusa, "conturi_in_afara": sorted(afara),
            # [425] rulajele anului: citite (și cu ce coloane) sau lipsă — cu ce afectează lipsa lor
            "rulaje": det.get("rulaje", False), "perechi": det.get("perechi", {}),
            "forma_rulaje": det.get("forma_rulaje"),   # [439] perechile cumulate: cu / fără soldul inițial al anului (din date)
            "avertisment_rulaje": None if det.get("rulaje") else solduri_api.avertisment_fara_rulaje(data_propusa),
            "cere_metoda_stoc": cere_metoda,
            "metode_stoc": [[_ms.GV, _ms.ETICHETE[_ms.GV]], [_ms.CV, _ms.ETICHETE[_ms.CV]]] if cere_metoda else [],
            # [426] balanța existentă (totalurile ei) și notele de după data balanței
            "existenta": existenta if existenta["are_solduri"] else None, "note_dupa": note,
            "avertisment_inlocuire": solduri_api.text_inlocuire(existenta, {"randuri": len(randuri), "total_debit": td,
                                                                            "total_credit": tc}, note, data_propusa)
            if existenta["are_solduri"] else None,
            **_firma_fisier(tenant_id, continut, nume_fisier)}   # [599] firma din antetul fișierului, față de firma aleasă
    if afara:
        return _uc_comun._raspuns(dict(baza, motiv=MESAJ_CONT_IN_AFARA % ", ".join(sorted(afara))))
    if valida:
        return _uc_comun._raspuns(dict(baza, motiv=motiv))
    from core.unde import Unde as _Unde
    return _uc_comun._raspuns(dict(baza, **migrare_api.respinge("balanță de deschidere", _Unde("fisier", nume_fisier or "(fără nume)"),
                                                                "balanta_nu_se_echilibreaza", motiv)))


def _firma_fisier(tenant_id, continut, nume_fisier):
    """[599] Firma din antetul fișierului de import, față de firma aleasă — sursa unică `uc_migrare.firma_fisier`, chemată de fiecare
    previzualizare de import de migrare (gard: `core/test_lot12_migr_firma_fisier.py`)."""
    from core import uc_migrare as _uc_migrare
    return _uc_migrare.firma_fisier(tenant_id, continut, nume_fisier)


def _data_soldurilor(conn, schema):
    """Data soldurilor de preluare ('YYYY-MM-DD') din sursa unică `bilant_api.data_soldurilor`, sau None (evidența întreagă în
    iConta.eu, fără preluare)."""
    from psycopg2.extras import RealDictCursor
    from core import bilant_api
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        d = bilant_api.data_soldurilor(cur, schema)
    return d.isoformat() if d else None


def parteneri_rezumat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return solduri_parteneri_api.rezumat(conn)


def parteneri_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]   # rand_fisier inclus: refuzul numește rândul din fișier
    with db.get_conn(schema) as conn:
        try:
            # [C22, clasa — 14.10.2026] data soldurilor pe parteneri = data soldurilor de preluare a firmei (sursa unică
            # `bilant_api.data_soldurilor`: data balanței, altfel ziua dinaintea lunii preluării). Ecranul nu trimitea niciodată
            # `data_referinta`, deci soldurile pe parteneri rămâneau fără dată.
            return solduri_parteneri_api.importa(conn, randuri, date.data_referinta or _data_soldurilor(conn, schema), schema=schema,
                                                 inlocuieste=bool(date.inlocuieste))
        except migrare_api.InlocuireNeconfirmata as e:   # [426, clasa] înlocuirea cere confirmare -> 409 cu totalurile vechi și noi
            raise _erori.Conflict(str(e))
        except ValueError as e:  # randuri invalide -> 422 cu mesaj explicativ
            raise _erori.DateInvalide(str(e))


def salariati_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return salariati_import_api.importa(conn, randuri, inlocuieste=bool(date.inlocuieste))
        except migrare_api.InlocuireNeconfirmata as e:   # [426, clasa] actualizarea fișelor existente cere confirmare -> 409
            raise _erori.Conflict(str(e))
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def istoric_cu_perioada(tenant_id, randuri, ctx):
    """[389, lotul 9] Perioada fiecărui rând din istoricul declarațiilor, cum o scrie formularul, după profilul firmei (trimestrial / lunar)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            pf = repo_firma_profil.profil_fiscal(cur)
    return istoric_declaratii_import_api.cu_perioada(randuri, {"tip_decont": pf[1], "regim_fiscal": pf[4]} if pf else {})


def asociati_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/asociati-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    anaf = asociati_import_api.verificare_anaf(randuri)   # [367] aceeași confruntare cu ANAF ca la previzualizare (poarta unică)
    with db.get_conn(schema) as conn:
        try:
            return asociati_import_api.importa(conn, randuri, data_cesiune=getattr(date, "data_cesiune", None), anaf=anaf,
                                               inlocuieste=bool(getattr(date, "inlocuieste", False)))
        except migrare_api.InlocuireNeconfirmata as e:   # [426, clasa] corectura peste asociații existenți cere confirmare -> 409
            raise _erori.Conflict(str(e))
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def asociati_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/asociati-import/incarca`. [comanda Costin 8.2 pct.4] fiecare rând citit, cu starea
    lui; [367] CUI-urile asociaților persoane juridice confruntate cu ANAF."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        randuri = asociati_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    anaf = asociati_import_api.verificare_anaf(randuri)
    asociati_import_api.eticheteaza(randuri, anaf)
    erori = migrare_api.erori_verifica(asociati_import_api.verifica_randuri(randuri, anaf))  # [Q5] poarta unica
    # [384] totalul cotelor din bandă = al rândurilor care intră (fără cele respinse pe rând), aceeași regulă ca salvarea
    _resp = {e.get("rand") for e in erori if isinstance(e.get("rand"), int)}
    # [426, clasa] „înainte de înlocuire: spune că există deja […], arată [structura] veche și nouă, cere confirmare” — pe rândurile care intră
    with db.get_conn(schema) as conn:
        existent = asociati_import_api.existent(conn)
    _nou = migrare_api.randuri_care_intra(randuri, erori)
    return _uc_comun._raspuns({"randuri": randuri, "total": len(randuri), "coerenta": asociati_import_api.coerenta_cote(randuri, _resp),
                               "erori": erori, "anaf_verificat": anaf is not None,
                               "existenta": existent if existent["randuri"] else None,
                               "avertisment_inlocuire": asociati_import_api.text_inlocuire(existent, _nou) if existent["randuri"] else None,
                               **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]


def retete_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            return retete_import_api.importa(conn, schema, [dict(r) for r in date.randuri])
        except ValueError as e:
            raise _erori.DateInvalide(str(e))


def articole_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/articole-import/incarca` — previzualizarea. [373] fiecare rând citit, cu starea
    lui; [374, comanda Costin 8.2: „ca la 359”] valoarea stocului pe fiecare cont de stoc față de balanța de deschidere."""
    import psycopg2.extras as _E
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        randuri = articole_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    with db.get_conn(schema) as conn:
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            solduri = solduri_api.solduri_deschidere(cur)
        data_sold = _data_soldurilor(conn, schema)
    # [lotul 13, deficiența 668] rândurile contului de stoc care nu dă soldul din balanța de deschidere nu intră — aceeași regulă la salvare
    articole_import_api.eticheteaza(randuri, solduri)
    return _uc_comun._raspuns({"randuri": randuri, "rezumat": articole_import_api.rezumat(randuri),
                               "erori": articole_import_api.verifica_randuri(randuri, solduri),
                               "reconciliere": articole_import_api.reconciliere_balanta(randuri, solduri),
                               "data_sold": data_sold, **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]


def articole_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/articole-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            # [C22, clasa — 14.10.2026] stocul inițial e „la” data soldurilor de preluare (sursa unică), nu la ziua importului:
            # ecranul nu trimitea `data_sold`, iar `importa` punea data de azi — mișcarea de intrare cădea în luna curentă.
            return articole_import_api.importa(conn, schema, randuri,
                                               data_sold=date.data_sold or _data_soldurilor(conn, schema))
        except (ValueError, KeyError) as e:    # [lotul 6] refuzul ajunge ca mesaj, nu ca 500
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))


def mijloace_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/mijloace-fixe-import`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            return mijloace_fixe_import_api.importa(conn, randuri, inlocuieste=bool(date.inlocuieste))
        except migrare_api.InlocuireNeconfirmata as e:   # [426, clasa] înlocuirea registrului cere confirmare -> 409 cu valorile
            raise _erori.Conflict(str(e))
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def mijloace_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Previzualizarea registrului de mijloace fixe (`POST /tenants/{tenant_id}/mijloace-fixe-import/incarca`).
    [359, comanda Costin 8.2] amortizarea preluată se compară la DATA PRELUĂRII (data soldurilor de deschidere), iar totalurile pe conturile
    2xx / 28xx se confruntă cu balanța de deschidere."""
    import psycopg2.extras as _E
    from core import bilant_api as _bil
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
            data_prel = _bil.data_soldurilor(cur, schema)
            solduri = solduri_api.solduri_deschidere(cur)
        existent = mijloace_fixe_import_api.existent(conn)   # [426, clasa] registrul existent și notele de amortizare de pe el
    try:
        randuri = mijloace_fixe_import_api.extrage(continut, nume_fisier, data_preluare=data_prel)
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    from decimal import Decimal as _D
    erori = migrare_api.erori_verifica(mijloace_fixe_import_api.verifica_randuri(randuri, data_prel))  # [Q5] poarta unica
    # [426, clasa] „înainte de înlocuire: spune că există deja […], arată totalurile vechi și noi, cere confirmare” — pe rândurile care intră
    _nou = mijloace_fixe_import_api.totaluri(migrare_api.randuri_care_intra(randuri, erori))
    return _uc_comun._raspuns({"randuri": randuri, "total": len(randuri), "erori": erori,
            "existenta": existent if existent["randuri"] else None,
            "avertisment_inlocuire": mijloace_fixe_import_api.text_inlocuire(existent, _nou) if existent["randuri"] else None,
            "inlocuire_refuzata": mijloace_fixe_import_api.refuz_inlocuire(existent),
            "total_valoare": float(sum((_D(str(r["valoare"] or 0)) for r in randuri), _D(0))),
            "respinse": sum(1 for r in randuri if r["stare"] == "respins"),
            "semnalate": sum(1 for r in randuri if r["stare"] == "semnalat"),
            "data_preluare": data_prel.isoformat() if data_prel else None,
            "reconciliere": mijloace_fixe_import_api.reconciliere_balanta(randuri, solduri), **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]


def istoric_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/istoric-declaratii-import`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn() as conn:
        try:
            return istoric_declaratii_import_api.importa(conn, tenant_id, randuri, inlocuieste=bool(date.inlocuieste))
        except migrare_api.InlocuireNeconfirmata as e:   # [426, clasa] înlocuirea istoricului preluat cere confirmare -> 409
            raise _erori.Conflict(str(e))
        except ValueError as e:  # randuri invalide -> 422 cu mesaj
            raise _erori.DateInvalide(str(e))


def istoric_inlocuire(tenant_id, randuri, erori, ctx):
    """[lotul 10, deficiența 426 — clasa] Previzualizarea istoricului: istoricul preluat deja existent și ce aduce fișierul (pe rândurile
    care intră) -> {existenta, avertisment_inlocuire}; amândouă None când firma n-are istoric preluat."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        vechi = istoric_declaratii_import_api.existent(conn, tenant_id)
    if not vechi["randuri"]:
        return {"existenta": None, "avertisment_inlocuire": None}
    nou = istoric_declaratii_import_api.totaluri(migrare_api.randuri_care_intra(randuri, erori))
    return {"existenta": vechi, "avertisment_inlocuire": istoric_declaratii_import_api.text_inlocuire(vechi, nou)}


def produse_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [lotul 11, 449] lista categoriilor cotei 0% și a bunurilor cu taxare inversă vine de aici (sursa: `categorii_tva`, `d394.CODPR`),
        # nu scrisă a doua oară în ecran
        return {"produse": produse_api.lista(conn), "categorii_tva": produse_api.categorii_pentru_ecran(),
                "categorii_331": produse_api.categorii_331_pentru_ecran()}


def produse_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [R193] faza de citire (produsul e deja în nomenclator?), apoi modelul cu pool-ul liber, apoi scrierea — care recitește
    with db.get_conn(schema) as conn:
        _de_intrebat = produse_api.de_intrebat(conn, date.denumire, date.cota_tva)
    _ai = cote_tva.intreaba(_de_intrebat)
    with db.get_conn(schema) as conn:
        r = produse_api.creeaza(conn, date.denumire, um=date.um,
                                pret_unitar=date.pret_unitar, cota_tva=date.cota_tva,
                                categorie=date.categorie, confirmat=date.confirmat, raspunsuri=_ai,
                                categorie_tva=date.categorie_tva, categorie_331=date.categorie_331)   # [lotul 11, 449]
    if not r.get("ok"):
        # [440] denumirea, UM-ul, prețul și categoria, toate deodată, fiecare lângă câmpul ei din Produse (`erori_campuri`)
        _ec = r.get("erori_campuri")
        raise _erori.CerereGresita({"mesaj": r["mesaj"], "erori_campuri": _ec} if _ec else r.get("mesaj", "produs invalid"))
    return r


def produse_actualizeaza(tenant_id, produs_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse/{produs_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = produse_api.actualizeaza(conn, produs_id, denumire=date.denumire,
                                     um=date.um, pret_unitar=date.pret_unitar,
                                     cota_tva=date.cota_tva, categorie=date.categorie,
                                     confirmat=date.confirmat,
                                     categorie_tva=date.categorie_tva, categorie_331=date.categorie_331)   # [lotul 11, 449]
    if r.get("erori_campuri"):   # [449, 440] refuzul datelor (categoria, denumirea, UM-ul, prețul — toate deodată), nu „produs inexistent”
        raise _erori.CerereGresita({"mesaj": r["mesaj"], "erori_campuri": r["erori_campuri"]})
    if r.get("cod") == "NIMIC":   # [440] cererea fără niciun câmp de schimbat nu e „produs inexistent”
        raise _erori.CerereGresita(r["mesaj"])
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


def facturi_numerotare_get(tenant_id, ctx, la_data=None):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/numerotare`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = facturi_api.numerotare(conn)
        # [comanda Costin 05.10.2026 pct.2–3] la DESCHIDEREA emiterii: ce lipsește din Date firmă (blochează emiterea), forma
        # propusă și cotele de TVA permise LA DATA FACTURII (din formular) — nu după completarea întregului formular. Fără
        # dată (alt ecran care cere doar numerotarea) nu se răspunde cu cote „de azi”.
        if la_data is not None:
            import datetime as _dt
            try:
                _d = _dt.date.fromisoformat(str(la_data))
            except ValueError:
                raise _erori.DateInvalide("Data emiterii nu e o dată calendaristică (aaaa-ll-zz): %r." % la_data)
            r.update(facturi_api.pregatire_emitere(conn, tenant_id, _d))
            # [lotul 11, deficiența 428] sistemul TVA la încasare LA DATA FACTURII (CF art.282 alin.(3), (7)): ecranul spune înainte de
            # emitere dacă TVA-ul merge pe 4428 cu mențiunea „TVA la încasare” sau rămâne la emitere — și de ce
            from core import tva_incasare as _tvi
            with conn.cursor() as _cur:
                r["tva_incasare"] = _tvi.regim_emitere_la(_cur, None, _d)
        return r


def facturi_numerotare_set(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/numerotare`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = facturi_api.seteaza_numerotare(conn, serie=date.serie, numar_start=date.numar_start)
    if not r.get("ok"):
        # [440] seria și numărul refuzate împreună, fiecare lângă câmpul lui (`erori_campuri`), nu numai fraza
        _ec = r.get("erori_campuri")
        raise _erori.CerereGresita({"mesaj": r["mesaj"], "erori_campuri": _ec} if _ec else r.get("mesaj", "eroare"))
    return r


def scadentar_get(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/scadentar`; docstringul ei a ramas in stratul HTTP."""
    from core import scadentar as _sc
    if ctx.get("rol") == "client":   # [lotul 13, 559] portalul: aceleași facturi ca „Cifrele firmei” (nota validată)
        from core import uc_portal as _uc_portal
        return _uc_portal.scadentar_client(tenant_id, ctx)
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
        # [R46] `platitor_tva` decide daca firma datoreaza D300/D394 si pe ce perioade. [05.10.2026] Poarta e pentru o
        # SCHIMBARE: aceeași valoare nu rescrie nimic și nu se refuză.
        with conn.cursor() as cur:
            _act = repo_firma_profil.regim_tva_pentru_schimbare(cur)
        if _act is not None and bool(_act["platitor_tva"]) != bool(date.platitor_tva):
            try:
                _fp.cere_perioade_deschise(conn, "Regimul de TVA")
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            repo_firma_profil.seteaza_platitor_tva(cur, date.platitor_tva, ctx["uid"])
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
        r = _fp.citeste_date(conn)
        # [comanda Costin 05.10.2026 pct.2] forma juridică necompletată -> propunerea neechivocă (ANAF / denumire), de confirmat
        if not (r.get("profil") or {}).get("forma_juridica"):
            r["forma_juridica_propusa"], r["forma_juridica_sursa"] = facturi_api.forma_propusa_firma(conn, tenant_id)
        with conn.cursor() as cur:   # [06.10.2026 §6.4] jurnalul Date firmă, vizibil cabinetului
            r["jurnal"] = repo_firma_profil.jurnal_firma(cur)
        return r


def firma_profil_date_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/date`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = _fp.salveaza_date(conn, date, tenant_id=tenant_id, user_id=ctx["uid"])   # [06.10.2026 §6.4] jurnalul cere autorul
    if not r.get("ok"):
        # [08.10 §6 pct.4, generalizat] refuzul își numește câmpul (`camp`), iar ecranul îl pune lângă el (DS cap.6, G10)
        # [lotul 11, deficiența 440] TOATE erorile adunate de `salveaza_date` (`erori_campuri`), nu numai prima
        _m = r.get("mesaj", "date invalide")
        _ec = r.get("erori_campuri") or ([{"camp": r["camp"], "mesaj": _m}] if r.get("camp") else None)
        raise _erori.DateInvalide({"mesaj": _m, "erori_campuri": _ec} if _ec else _m)
    return r


def firma_cui_corectura(tenant_id, cui, confirmat, ctx):
    """[deficiența 272] Corpul rutei `/tenants/{tenant_id}/cui/corectura`. Avertismentul (fără confirmare) e un răspuns, nu un refuz."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [459] datele ANAF ale CUI-ului NOU, cerute ÎNAINTE de conexiune (P5 val 3: termenul ANAF e 20 s) și numai pentru un CUI valabil
    # (unul greșit nu pleacă la ANAF: „negăsit” ar fi fals); corectura le propune, iar confirmarea le aplică (`corecteaza_cui`)
    _anaf, _anaf_eroare = None, None
    if not tenant_provisioning.motiv_cui_firma_invalid(cui):
        try:
            _anaf = tenant_provisioning.date_din_anaf(cui)
        except Exception as _e:
            from core import anaf_api as _aa
            _obs.esec_secundar("datele ANAF la corectura CUI-ului", _e)
            _anaf_eroare = _aa.mesaj_indisponibil(_e)
    with db.get_conn(schema) as conn:
        r = _fp.corecteaza_cui(conn, tenant_id, cui, ctx["uid"], confirmat=confirmat, anaf=_anaf, anaf_eroare=_anaf_eroare)
        if r.get("cod") == "CONFIRMARE_CERUTA":
            return r
        if not r.get("ok"):
            _m = r.get("mesaj", "date invalide")
            raise _erori.DateInvalide({"mesaj": _m, "erori_campuri": [{"camp": r["camp"], "mesaj": _m}]} if r.get("camp") else _m)
    return r


def firma_profil_model(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/firma-profil/model`; docstringul ei a ramas in stratul HTTP."""
    import re as _re
    if date.culoare and not _re.fullmatch(r"#[0-9a-fA-F]{6}", date.culoare.strip()):
        raise _erori.DateInvalide("Culoarea se scrie ca un cod hexazecimal de șase cifre, cu diez "
                                     "(de exemplu #1d4ed8) — s-a primit %r. Ea ajunge pe factura "
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
    _ai = _uc_comun._intreaba_modelul(schema, (corp or {}).get("linii") or [])   # [462] ca la emitere: modelul înaintea conexiunii
    with db.get_conn() as conn:
        r = _fr.adauga(conn, schema, corp, raspunsuri_ai=_ai)
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


def facturi_storno(tenant_id, factura_id, ctx, corp=None):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/storno`; docstringul ei a ramas in stratul HTTP.
    [419] `corp.retur`: true (marfa se întoarce în stoc) / false (rămâne la client); obligatoriu la factura care a descărcat stocul."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    retur = (corp or {}).get("retur")
    refuz = "„retur” e da sau nu (true / false)." if retur is not None and not isinstance(retur, bool) else None
    if not refuz:
        with db.get_conn(schema) as conn:
            try:
                return facturi_api.storneaza(conn, factura_id, retur=retur)
            except ValueError as e:
                if getattr(e, "cod", None) != facturi_api.COD_CERE_RETUR:
                    raise _erori.DateInvalide(str(e))
                refuz = {"mesaj": str(e), "cod": facturi_api.COD_CERE_RETUR, "camp": "fd-storno-retur"}   # [419] întrebarea retur
    raise _erori.DateInvalide(refuz)


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
                                         tva_data_inceput=date.tva_data_inceput,  # [tva_inceput] data manuala INTAI
                                         user_id=ctx["uid"])  # [PIVOT 04.10.2026] jurnalul regimului de TVA
        # [tva_inceput] ANAF autoritar CAND are data: seteaza_snapshot_tva o suprascrie. Cand ANAF nu raspunde
        # (anaf_val None, gasit=False) NU se cheama deloc -> data manuala ramane. Cand ANAF raspunde dar NU are
        # data (tva_inceput None), guard-ul din seteaza_snapshot_tva NU goleste coloana -> data manuala ramane.
        if rez.get("ok") and anaf_val is not None:     # salvat + ANAF a raspuns -> snapshot (+ data inceput TVA)
            _fp.seteaza_snapshot_tva(conn, anaf_val, tva_inceput)
    if not rez.get("ok"):
        _mesaj = rez.get("mesaj", "vector invalid")
        _camp = rez.get("camp")
        if _camp:   # Regula 14.4 pct.4: marcheaza campul vinovat, nu doar mesaj generic ([lotul 11, 440]: toate câmpurile)
            raise _erori.CerereGresita({"mesaj": _mesaj, "erori_campuri": rez.get("erori_campuri") or [{"camp": _camp, "mesaj": _mesaj}]})
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
        _fti = _anaf.furnizor_incasare_freeze(date.tert_cui, fallback=bool(date.furnizor_tva_incasare), data=date.data_emitere)  # [3j] statutul la data emiterii
    try:
        with db.get_conn(schema) as conn:
            r = facturi_api.creeaza_factura(
                conn, date.numar, date.data_emitere, date.directie, linii,
                client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, data_scadenta=date.data_scadenta,
                moneda=date.moneda, status=date.status,
                tert_tara=date.tert_tara, tip_operatiune=date.tip_operatiune,
                furnizor_tva_incasare=_fti,
                categorie_331=date.categorie_331)   # [274b] la emise: categoria produsului când o linie e cu taxare inversă
    except facturi_api.FacturaRefuzata as e:   # [lotul 11, 440] toate refuzurile de formă, fiecare cu câmpul ei
        raise _erori.DateInvalide(e.detaliu())
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
        # [lotul 10, 428, decizia „Bifă pe client”] și beneficiarii facturilor emise fără fișă de client: bifa „persoană afiliată” se pune
        # și pe ei (ecranul `clienti_ecran.js` le creează fișa la salvare)
        # [lotul 11, decizia 10.3] + județele (codul pe care îl păstrează fișa, cu numele lui — aceeași listă ca factura)
        from core.factura_pdf import JUDETE_NUME
        return {"clienti": clienti_api.lista_clienti(conn, status), "parteneri_fara_fisa": clienti_api.parteneri_fara_fisa(conn),
                "judete": sorted(([k, v] for k, v in JUDETE_NUME.items()), key=lambda x: x[1])}


def _refuz_fisa(e):
    """[lotul 11] Refuzul unei valori din fișa partenerului (`clienti_api._curata`: județul), lângă câmpul ei (G10)."""
    camp = getattr(e, "camp", None)
    return _erori.DateInvalide({"mesaj": str(e), "erori_campuri": [{"camp": camp, "mesaj": str(e)}]} if camp else str(e))


def client_creeaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return clienti_api.creeaza_client(conn, **date.model_dump())
    except _chei.CheieDublata as e:   # [lotul 10, C73] CUI deja în nomenclator -> 409 cu clientul existent (nu 500)
        raise _erori.Conflict(e.detaliu())
    except ValueError as e:
        if getattr(e, "camp", None):   # [lotul 11] valoarea refuzată are câmp (județul): refuzul stă lângă el
            raise _refuz_fisa(e)
        raise _erori.DateInvalide(str(e))


def parteneri_lista(tenant_id, ctx):
    """[lotul 12, 461] GET `/tenants/{tenant_id}/parteneri` — partenerii firmei din toate documentele (`clienti_api.parteneri_firmei`)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        return {"parteneri": clienti_api.parteneri_firmei(conn, schema)}


def parteneri_fisa(tenant_id, cheie, ctx):
    """[lotul 12, 461] GET `/tenants/{tenant_id}/parteneri/fisa` — fișa partenerului: datele, documentele, soldul din contabilitate."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        f = clienti_api.fisa_partenerului(conn, schema, cheie)
    if f is None:
        raise _erori.Inexistent("Partenerul nu apare în documentele firmei.")
    return f


def furnizori_lista(tenant_id, status, ctx):
    """[lotul 11, decizia Costin 10.3 pct.4] `/tenants/{tenant_id}/furnizori`: fișele furnizorilor și furnizorii facturilor primite (și
    ai borderourilor de achiziție) fără fișă — localitatea și județul lor se completează aici (D406 / D394 le citesc din fișă)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    from core.factura_pdf import JUDETE_NUME
    with db.get_conn(schema) as conn:
        return {"furnizori": clienti_api.lista_furnizori(conn, status),
                "parteneri_fara_fisa": clienti_api.parteneri_fara_fisa(conn, "furnizori"),
                "judete": sorted(([k, v] for k, v in JUDETE_NUME.items()), key=lambda x: x[1])}


def furnizor_creeaza(tenant_id, date, ctx):
    """[lotul 11, decizia 10.3] POST `/tenants/{tenant_id}/furnizori` — fișa nouă (CUI deja în fișe -> 409 cu furnizorul existent)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        with db.get_conn(schema) as conn:
            return clienti_api.creeaza_furnizor(conn, **date.model_dump())
    except _chei.CheieDublata as e:
        raise _erori.Conflict(e.detaliu())
    except ValueError as e:
        raise _refuz_fisa(e)


def furnizor_actualizeaza(tenant_id, furnizor_id, date, ctx):
    """[lotul 11, decizia 10.3] PUT `/tenants/{tenant_id}/furnizori/{furnizor_id}` — numai câmpurile trimise; inexistent -> 404."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        if not clienti_api.detalii_furnizor(conn, furnizor_id):
            raise _erori.Inexistent("Furnizorul nu există (fișa a fost ștearsă?).")
        try:
            return clienti_api.actualizeaza_furnizor(conn, furnizor_id, **date.model_dump())
        except _chei.CheieDublata as e:
            raise _erori.Conflict(e.detaliu())
        except ValueError as e:
            raise _refuz_fisa(e)


def cui_firma_invalid(cui):
    """[459, comanda Costin 11.3 pct.5] Răspunsul verificării publice (`GET /public/verifica-cui`, ecranele „Adaugă firmă” și înregistrarea)
    pentru un CUI de firmă care nu e valabil: {gasit: False, cui_invalid: True, motiv} — ÎNAINTE de ANAF (un CUI greșit nu pleacă la ANAF:
    „negăsit” ar fi fals, iar ecranul l-ar lăsa să treacă la „completează denumirea manual”). None când CUI-ul e valabil.

    [lotul 11, AT] Validarea CÂMPULUI CUI din formular (motivul se pune lângă câmp), nu o afirmație despre datele firmei: `camp` = câmpul,
    ca `tenant_provisioning.CuiInvalid.camp` și refuzurile 273c — clasa D din `scan_afirmatii`, în afara deciziei din 21.08."""
    m = tenant_provisioning.motiv_cui_firma_invalid(cui)
    return {"gasit": False, "cui_invalid": True, "cui": cui, "camp": tenant_provisioning.CuiInvalid.camp, "motiv": m} if m else None


def verifica_cui(tenant_id, cui, nume, ctx):
    """[P7 · use-case] Corpul rutei GET `/tenants/{tenant_id}/verifica-cui/{cui}` — o CITIRE: verificarea la ANAF (`anaf_api.valideaza_cui`)
    și, [lotul 11, deficiența 444], fișele firmei cu acel CUI și diferența de nume (`clienti_api.compara_cu_anaf`), chemată de fișă,
    factură, NIR, casă. `nume` = numele scris pe ecran: `nume_dat_diferit` spune dacă diferă de ANAF (`clienti_api.nume_diferit`).
    [lotul 11, K] Corpul a venit întreg aici (ruta e înveliș): ruta pe jumătate în HTTP, pe jumătate delegată unui use-case cu alt nume,
    nu se mai putea urmări funcție cu funcție, iar atribuirea scrierilor cădea pe modul — „GET verifica-cui scrie 78 de tabele”
    (`core/test_atribuire_scrieri.py`)."""
    from core import anaf_api
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)  # doar verific accesul
    try:
        rez = anaf_api.valideaza_cui([cui])
    except Exception as e:
        raise _erori.ServiciuStrainCazut(anaf_api.mesaj_indisponibil(e))   # [303 + 317] 502
    if not rez:
        return {"gasit": False}
    rez = rez[0]
    if not (rez and rez.get("gasit")):
        return rez
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        return dict(rez, **clienti_api.compara_cu_anaf(cur, rez.get("cui"), rez.get("denumire")),
                    nume_dat_diferit=clienti_api.nume_diferit(nume, rez.get("denumire")))


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
        try:
            return clienti_api.actualizeaza_client(conn, client_id, **date.model_dump())
        except _chei.CheieDublata as e:   # [lotul 10, C73] CUI-ul altui client -> 409 cu clientul care îl are (nu 500)
            raise _erori.Conflict(e.detaliu())
        except ValueError as e:   # [lotul 11] județul necunoscut, numele golit -> refuz numit, lângă câmp
            raise _refuz_fisa(e)


def client_sterge(tenant_id, client_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/clienti/{client_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = clienti_api.sterge_client(conn, client_id)
    if not r["ok"] and r.get("cod") == "ARE_FACTURI":
        raise _erori.Conflict(r["mesaj"])
    return r


def furnizor_sterge(tenant_id, furnizor_id, ctx):
    """[lotul 13, 640] Corpul rutei `DELETE /tenants/{tenant_id}/furnizori/{furnizor_id}`, ca `client_sterge`: fișa furnizorului fără facturi
    primite / borderouri se șterge (`clienti_api.sterge_furnizor`); inexistentă -> 404, cu documente -> 409."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = clienti_api.sterge_furnizor(conn, furnizor_id)
    if not r.get("ok"):
        if r.get("cod") == "INEXISTENT":
            raise _erori.Inexistent(r["mesaj"])
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
            corp = date.model_dump()
            if corp.get("salariu_brut") is not None:
                # [salariul în timp, decizia Costin 04.10.2026] data validată ÎNAINTE de scriere; fiecare lună atinsă
                # de schimbare (de la data ei până la următoarea intrare din istoric / azi) trece prin poarta de
                # perioadă — o lună închisă nu se rescrie pe ușa salariului.
                import datetime as _dtm
                d, ultima = salariati_api.valideaza_schimbare_salariu(
                    conn, salariat_id, corp["salariu_brut"], corp.get("valabil_din"), corp.get("inlocuieste") is True,   # bool deja (SalariatEdit, pydantic)
                    corp.get("data_angajare"), corp.get("data_incetare"))
                capat = min(ultima or _dtm.date.today(), _dtm.date.today())
                y, m = d.year, d.month
                while (y, m) <= (capat.year, capat.month):
                    _uc_comun._cere_luna_deschisa(conn, schema, "%04d-%02d-01" % (y, m))
                    y, m = (y + 1, 1) if m == 12 else (y, m + 1)
                corp["valabil_din"] = d.isoformat()
            rez = salariati_api.actualizeaza_salariat(conn, salariat_id, _golite=golite, **corp)
            if trimise.get("suspendari") is not None:
                # [lot 19 pct.4c] CFP / suspendare -> statul de plată și D112 proratează brutul (Codul muncii art.49
                # alin.(2)). Lunile atinse de o schimbare trec prin aceeași poartă de perioadă ca orice înregistrare.
                noi = salariati_api.valideaza_suspendari(conn, salariat_id, trimise["suspendari"])
                with conn.cursor() as cur:
                    vechi = [tuple(r)[1:5] for r in repo_salariati.suspendari_salariat(cur, salariat_id)]
                for a, b, *_ in set(vechi) ^ set(noi):
                    y, m = a.year, a.month
                    while (y, m) <= (b.year, b.month):
                        _uc_comun._cere_luna_deschisa(conn, schema, "%04d-%02d-01" % (y, m))
                        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
                salariati_api.seteaza_suspendari(conn, salariat_id, noi)
                rez = dict(rez, suspendari=len(noi))
            return rez
    except ValueError as e:
        _ec = getattr(e, "erori_campuri", None)  # [G10] contract {detail, erori_campuri}
        if getattr(e, "cod", None) == salariati_api.COD_DATA_OCUPATA:
            # [salariul în timp] refuz STRUCTURAT: ecranul arată intrarea existentă și oferă înlocuirea explicită
            raise _erori.DateInvalide({"mesaj": str(e), "erori_campuri": _ec, "cod": e.cod, "existent": e.existent})
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
            # [lotul 11, 440] toate erorile beneficiului (evenimentul, valoarea, multiplul de 10, plafonul), fiecare cu câmpul ei
            raise _erori.CerereGresita({"mesaj": r["eroare"], "erori_campuri": r["erori_campuri"]} if r.get("erori_campuri")
                                       else r["eroare"])
        return r


def salariat_elemente(tenant_id, salariat_id, an, luna, ctx):
    """[S1] Corpul rutei `GET /tenants/{tenant_id}/salariati/{salariat_id}/elemente`."""
    _uc_comun._cere_perioada(an, luna)
    from core import elemente_salariale as _es
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        el = _es.lista_luna(conn, schema, an, luna, salariat_id).get(int(salariat_id), [])
    return {"elemente": el, "total": str(_es.total(el)), "tipuri": _es.TIPURI}


def salariat_element_adauga(tenant_id, salariat_id, corp, ctx):
    """[S1] Corpul rutei `POST /tenants/{tenant_id}/salariati/{salariat_id}/elemente`. Luna închisă sau cu D112 depusă: refuz."""
    from core import elemente_salariale as _es
    an, luna = corp.get("an"), corp.get("luna")
    if not isinstance(an, int) or not isinstance(luna, int) or luna < 1 or luna > 12:
        raise _erori.CerereGresita("Luna elementului de salariu nu e validă.")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        _uc_comun._cere_luna_deschisa(conn, schema, _uc_comun.ultima_zi_a_lunii(an, luna))
        r = _es.adauga(conn, schema, salariat_id, an, luna, corp, tenant_id=tenant_id)
        if r.get("cod") == "INEXISTENT":
            raise _erori.Inexistent(r["mesaj"])
        if not r["ok"]:
            raise _erori.DateInvalide({"mesaj": r["mesaj"], "erori_campuri": r["erori_campuri"]} if r.get("erori_campuri")
                                      else r["mesaj"])
        return r


def salariat_element_sterge(tenant_id, salariat_id, element_id, ctx):
    """[S1] Corpul rutei `DELETE /tenants/{tenant_id}/salariati/{salariat_id}/elemente/{element_id}`."""
    from core import elemente_salariale as _es
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r0 = _es.luna_elementului(conn, schema, element_id)
        if r0:
            _uc_comun._cere_luna_deschisa(conn, schema, _uc_comun.ultima_zi_a_lunii(r0[0], r0[1]))
        r = _es.sterge(conn, schema, salariat_id, element_id, tenant_id=tenant_id)
        if not r["ok"]:
            raise (_erori.Inexistent if r.get("cod") == "INEXISTENT" else _erori.Conflict)(r["mesaj"])
        return r


def salariat_sterge(tenant_id, salariat_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        r = salariati_api.sterge_salariat(conn, salariat_id)
    if not r["ok"] and r.get("cod") == "ARE_CONCEDII":
        raise _erori.Conflict(r["mesaj"])
    return r


#: [deficiența 274a] articolul de stoc fără produs (sau fără cotă) în nomenclator: ce se spune pe linie, cu butonul spre Produse
COD_ARTICOL_FARA_COTA = "ARTICOL_FARA_COTA"
MESAJ_ARTICOL_FARA_COTA = ("Articolul „%s” n-are cota TVA în nomenclator, deci nu se propune nicio cotă. Adaug-o în Produse (o dată, pentru "
                           "toate facturile), sau alege cota pe linie.")


def produse_potriveste(tenant_id, denumire, ctx, din_articol=False):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/produse/potriveste`. [lot 19 pct.4d] Statutul de plătitor TVA
    se citește din profilul firmei, nu din cerere: cererea fără câmp primea implicit True, deci un neplătitor primea
    propus 21% (CF art.310 alin.(10) lit.b): neplătitorul „nu are voie să menționeze taxa pe factură”).
    [deficiența 274a, comanda Costin 16.10.2026, verbatim în DECIZII] „Cota vine de la articolul din nomenclator; dacă articolul n-are
    cotă, mesajul spune asta și trimite la Produse.” `din_articol`: linia are articol de stoc (Marfa A) — cota numai din nomenclator,
    fără potrivirea automată; lipsa ei e un răspuns cu motivul și ținta `produse`, nu o linie „—” tăcută."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    if din_articol:
        with db.get_conn(schema) as conn:
            platitor = _uc_comun._platitor_tva_firma(conn)
            p = produse_api.cauta_dupa_denumire(conn, denumire)
        if platitor and (not p or p.get("cota_tva") is None):
            _m = MESAJ_ARTICOL_FARA_COTA % (denumire or "").strip()
            return dict(_af.afirmatie("absenta_observatie", "cota_articol", _m, surse_consultate=["nomenclatorul Produse"]),
                        ok=False, cod=COD_ARTICOL_FARA_COTA, mesaj=_m, ecran="produse")
    # [R193] citirea (plătitorul, nomenclatorul), apoi modelul cu pool-ul liber, apoi propunerea, care recitește nomenclatorul
    with db.get_conn(schema) as conn:
        platitor = _uc_comun._platitor_tva_firma(conn)
        _de_intrebat = produse_api.de_intrebat(conn, denumire) if platitor else []
    _ai = cote_tva.intreaba(_de_intrebat, platitor)
    with db.get_conn(schema) as conn:
        # [05.10.2026, comanda Costin pct.9] nomenclatorul firmei întâi (cota, UM, preț), potrivirea automată după
        out = produse_api.propunere_pentru_linie(conn, denumire, platitor_tva=platitor, raspunsuri=_ai)
    # [deficiența 326, 18.10.2026] felul liniei (marfă / produse / servicii), în aceeași ordine ca la emitere (`facturi_api`, contul de
    # venit): cuvântul-cheie întâi, apoi răspunsul modelului. Ecranul propune din el categoria art.278 alin.(2) și UM-ul serviciului.
    if isinstance(out, dict) and out.get("ok"):
        from core import facturi as _fc
        out["tip"] = _fc.tip_din_denumire(denumire) or out.get("tip")
    return out


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            urme = [dict(x) for x in repo_utilizatori.urme_portal_ale_firmei(cur, tenant_id)]
    return {"urme": urme, "nr": len(urme)}


def bonuri_de_verificat(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/de-verificat`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            bonuri = [{"id": r[0], "comerciant": r[1], "cui": r[2],
                       "data": r[3].isoformat() if r[3] else None,
                       "total": float(r[4] or 0),
                       "tva": (round(sum(float(x.get("valoare") or 0) for x in r[13]), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            iid = repo_contabilitate.nota_bon_ciorna(cur, schema, b.data, f"BON-{bon_id}", f"Bon {b.comerciant}",
                                                       _jurnal_api.eticheta_document("Bon fiscal", None, b.data, b.comerciant))[0]
            for l in b.linii:
                # [280] valoarea fără TVA a liniei e o sumă nouă, intră în notă: rotunjire aritmetică (`common._q`), nu `round()` la par
                repo_contabilitate.adauga_linie_credit_casa(cur, schema, iid, l.cont,
                                                            float(_common._q(_common._dec(l.valoare) * _common._dec(factor))))
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
    from core import eticheta_nota as _et
    with db.get_conn(schema) as conn, conn.cursor() as cur:
        r = repo_contabilitate.id_nota_dupa_numar(cur, p["document_ref"])
        p["nota_eticheta"] = _et.nota(cur, schema, r[0]) if r else None   # [258] ecranul numește nota ca jurnalul, nu prin id
    p["deja_contata"] = bool(r)
    p["nota_id"] = r[0] if r else None
    from core import inchidere_luna as _il   # [deficiența 216] ecranul spune de ce nota nu se scrie încă, în loc să ofere butonul
    p["neincheiata"] = _il.luna_in_curs(an, luna)
    # [validare_note, comanda Costin 06.10.2026 pct.1] statul de plată arată unde e nota în coada de validare
    if r:
        from core import coada_api as _coada
        with db.get_conn() as conn:
            p["validare"] = _coada.stari_note(conn, tenant_id, [r[0]]).get(r[0])
        # [retest 08.10 pct.1] ciorna nevalidată cu alte sume (sau altă dată) decât nota din statul afișat: ecranul o spune și oferă
        # înlocuirea — „nu rămâne niciodată o ciornă cu alte sume decât statul afișat”
        from core import note_derivate as _nd
        with db.get_conn(schema) as conn, conn.cursor() as cur:
            p["ciorna_alte_sume"] = bool(_nd.ciorna_nevalidata(cur, schema, r[0]) and repo_contabilitate.liniile_si_data(cur, r[0])
                                         != (str(_uc_comun.ultima_zi_a_lunii(an, luna)),
                                             sorted((n["debit"], n["credit"], "%.2f" % n["suma"]) for n in p["note"])))
    return p


def tenant_amortizare(tenant_id, an, luna, ctx, refuza_aceeasi=True):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/amortizare`; docstringul ei a ramas in stratul HTTP.
    [lotul 11, comanda 11.1 pct.23: „«Generează amortizarea» activ pe luni deja amortizate”] a doua generare a aceleiași note se REFUZĂ,
    numită: nota validată (ca înainte) și ciorna care are deja exact sumele registrului de acum (`refuza_aceeasi`; până acum se întorcea
    tăcut aceeași ciornă, iar ecranul spunea „Notă generată”). Ciorna cu alte sume se înlocuiește în continuare (decizia 08.10 §6 pct.6).
    `tenant_amortizare_restanta` cheamă cu `refuza_aceeasi=False`: lunile la zi le numără separat („deja generate”, deficiența 312).
    Răspunsul poartă eticheta notei și rândurile ei (`linii_nota`), pentru confirmarea unică a ecranului (`api.dupaGenerare`, 8c)."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 7] `luna=13` dadea `500`, pe o ruta care scrie EVIDENTA
    _uc_comun._cere_luna_incheiata(an, luna, "Amortizarea lunii")   # [deficiența 216, aceeași clasă]
    from datetime import date as _date
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [R42 (a)] Nota de amortizare se datează în ULTIMA zi a lunii cerute (lotul 07.10 pct.7: ziua 28 n-avea temei).
        _uc_comun._cere_luna_deschisa(conn, schema, _uc_comun.ultima_zi_a_lunii(an, luna))
        ref = _date(an, luna, 1)
        from core import amortizare_lunii as _al
        numar = _al.numar(an, luna)
        ciorna_veche = doc_vechi = None
        with conn.cursor() as cur:
            # [08.10.2026, decizia Costin §6 pct.6] „Amortizarea și descărcarea GV: aceeași regulă ca T1 — înlocuire automată a ciornei
            # nevalidate; ce e validat nu se atinge.” Nota respinsă se înlocuiește la fel (ca la stat, lotul 07.10 B C9).
            from core import note_derivate as _nd
            ex = repo_contabilitate.nota_de_amortizare(cur, schema, numar)
            if ex:
                if _nd.respinsa(cur, schema, ex[0]):
                    doc_vechi = repo_contabilitate.documentul_notei(cur, schema, ex[0])
                    _nd.sterge_respinsa(cur, schema, ex[0])
                elif _nd.ciorna_nevalidata(cur, schema, ex[0]):
                    ciorna_veche = ex[0]
                    doc_vechi = repo_contabilitate.documentul_notei(cur, schema, ex[0])
                    repo_contabilitate.punct_de_revenire(cur, "amortizare_ciorna")
                else:
                    from core import eticheta_nota as _et   # [deficiența 258] nota cum o vede omul, nu id-ul ei
                    raise _erori.CerereGresita("Amortizarea lunii e deja generată și validată (nota %s) — nota validată nu se "
                                               "înlocuiește; o corectură se face printr-o altă notă." % _et.nota(cur, schema, ex[0]))
            # [lotul 11, 451] rândurile din sursa unică `amortizare_lunii.linii` (metoda reală, CF art.28) — aceeași cu regenerarea pe
            # uscat a ciornei la validare (`ciorne_depasite`)
            try:
                linii = _al.linii_cu_activ(cur, schema, an, luna)   # [lotul 13, 522] fiecare rând cu activul lui
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            if not linii:
                if ciorna_veche:   # registrul nu mai are nimic de amortizat: ciorna veche nu mai are temei
                    _nd.sterge_ciorna_inlocuita(cur, schema, ciorna_veche)
                return {"ok": True, "mesaj": "nimic de amortizat", "linii": 0, "inlocuita": ciorna_veche}
            iid = repo_contabilitate.nota_amortizare_ciorna(
                cur, schema, _uc_comun.ultima_zi_a_lunii(an, luna), numar, f"Amortizare {luna:02d}/{an}", doc_vechi)[0]
            from core import mf_note as _mfn
            for cont_am, rata, den, mid in linii:
                _mfn.adauga_linie(cur, schema, iid, _al.CONT_CHELTUIALA, cont_am, rata, mid)
            reluare = _reluare_subventii(cur, schema, an, luna, linii)   # [lotul 13, 528] subvențiile activelor, odată cu amortizarea
            if ciorna_veche:
                from core import coada_api as _cq
                if _cq.amprente_note(cur, [ciorna_veche], schema) == _cq.amprente_note(cur, [iid], schema):
                    repo_contabilitate.revino_la(cur, "amortizare_ciorna")   # aceleași sume: ciorna e chiar registrul de acum
                    if refuza_aceeasi:
                        from core import eticheta_nota as _et
                        raise _erori.CerereGresita("Amortizarea lunii e deja generată, cu exact sumele registrului de acum (nota %s, "
                                                   "ciornă) — o vezi și o validezi în Registru jurnal; o a doua generare n-ar schimba "
                                                   "nimic." % _et.nota(cur, schema, ciorna_veche))
                    return {"ok": True, "nota_id": ciorna_veche, "linii": len(linii), "deja_generata": True,
                            "total": round(sum(r for _, r, _, _m in linii), 2)}  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
                _nd.sterge_ciorna_inlocuita(cur, schema, ciorna_veche)
            from core import eticheta_nota as _et
            eticheta = _et.nota(cur, schema, iid)
    return {"ok": True, "nota_id": iid, "nota_eticheta": eticheta, "linii": len(linii),
            "linii_nota": [{"debit": "6811", "credit": c, "suma": s} for c, s, _d, _m in linii],   # [8c] rândurile notei, ca la scriere
            "total": round(sum(r for _, r, _, _m in linii), 2), "inlocuita": ciorna_veche,  # round-ok: sumă de bani deja rotunjiți
            "reluare_subventii": reluare}  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5


def perioade_blocate_lista(tenant_id, ctx, an=None, luna=None):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate`; docstringul ei a ramas in stratul HTTP.
    [08.10.2026, W2 + W3] Cu `an` + `luna`: și controalele închiderii acelei luni (ecranul „Închidere lună” le arată înainte de
    blocare — aceleași pe care le aplică poarta)."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            out = {"blocate": [{"an": r[0], "luna": r[1]} for r in repo_contabilitate.perioade_blocate(cur, schema)]}
        if an and luna:
            out["controale"] = _uc_comun.controale_inchidere(conn, schema, int(an), int(luna))
            conn.rollback()   # citire: controalele nu scriu nimic (search_path local se aruncă odată cu tranzacția)
        return out


def perioada_blocheaza(tenant_id, an, luna, ctx, confirma_amortizare=False):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/perioade-blocate`; docstringul ei a ramas in stratul HTTP.
    [deficiența 281] `confirma_amortizare`: confirmarea explicită care trece peste blocajele CONFIRMABILE (amortizarea lunilor anterioare
    neînregistrată); ea se consemnează în urma închiderii (`perioade_inchideri.motiv`), cu mesajele trecute."""
    from core import migrare_inchideri as _ui
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [08.10.2026, W2 + W3] controalele închiderii, o singură definiție (și pentru ecranul „Închidere lună”)
        ctl = _uc_comun.controale_inchidere(conn, schema, an, luna)
        trecute = [b for b in ctl["blocaje"] if confirma_amortizare and b.get("confirmabil")]
        ctl = dict(ctl, blocaje=[b for b in ctl["blocaje"] if b not in trecute])
        if ctl["blocaje"]:
            # Refuzul spune CE oprește și UNDE se rezolvă — nu doar că nu se poate.
            motive = [b["mesaj"] for b in ctl["blocaje"]]
            ciorne = next((1 for b in ctl["blocaje"] if b["cod"] == "CIORNE"), 0)
            facturi_desch = next((1 for b in ctl["blocaje"] if b["cod"] == "FACTURI_NEINCHEIATE"), 0)
            bl = next((b["mesaj"] for b in ctl["blocaje"] if b["cod"] == "EFACTURI"), None)
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
                    motive=motive, ciorne=ciorne, facturi=facturi_desch, blocaj=bl, blocaje=ctl["blocaje"],
                    semnale=ctl["semnale"]))
        with conn.cursor() as cur:
            repo_contabilitate.blocheaza_perioada(cur, schema, an, luna, ctx["uid"])
        _ui.scrie(conn, schema, an, luna, "inchisa", ctx["uid"],
                  motiv=("închisă cu confirmare explicită: " + "; ".join(b["mesaj"] for b in trecute)) if trecute else None)
        conn.commit()
    return {"blocat": f"{luna:02d}/{an}", "semnale": ctl["semnale"], "confirmate": [b["mesaj"] for b in trecute]}


def tenant_amortizare_restanta(tenant_id, an, luna, ctx):
    """[deficiența 281, comanda Costin 16.10.2026, verbatim în DECIZII] „lunile de amortizare restante după preluare (01–08/2026) se
    generează cu o singură acțiune, cu câte o notă pe lună, nu lună cu lună.” Lunile: cele dinaintea lui (an, luna) cu amortizarea
    neînregistrată (`mf_registru.luni_anterioare_neinregistrate` — aceeași regulă ca blocajul închiderii, fără lunile acoperite de
    soldul preluat) și luna însăși, dacă și ea lipsește. Fiecare lună trece prin `tenant_amortizare` (aceeași notă, aceleași porți: luna
    încheiată, luna deschisă, ciorna înlocuită, validatul neatins). O lună refuzată nu le oprește pe celelalte: refuzul ei se întoarce."""
    _uc_comun._cere_perioada(an, luna)
    from core import mf_registru as _mfr, repo_mijloace_fixe as _rmf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            repo_contabilitate.search_path_firma(cur, schema)
            rows = _rmf.toate(cur)
            luni = {l for x in _mfr.luni_anterioare_neinregistrate(cur, rows, an, luna) for l in x["luni"]}
            if any(x.get("rata") is not None for x in _mfr.amortizare_lunii_neinregistrata(cur, rows, an, luna)):
                luni.add((an, luna))
        conn.rollback()
    out = []
    for a, l in sorted(luni):
        try:
            # [lotul 13, deficiența 517] luna cu nota ei deja VALIDATĂ, în care lipsește un activ (adăugat după ea): rândurile lui intră
            # într-o notă separată, pe activ — nota validată nu se înlocuiește
            sup = _amortizare_suplimentara(tenant_id, a, l, ctx)
            if sup is not None:
                out.append(sup)
                continue
            r = tenant_amortizare(tenant_id, a, l, ctx, refuza_aceeasi=False)   # [lotul 11] lunile la zi se numără, nu se refuză
            out.append({"an": a, "luna": l, "ok": True, "nota_id": r.get("nota_id"), "total": r.get("total"),
                        "deja_generata": bool(r.get("deja_generata")),
                        "nota_eticheta": r.get("nota_eticheta"), "linii_nota": r.get("linii_nota") or []})   # [8c] rândurile notei
        except _erori.EroareDeDomeniu as e:
            det = e.detaliu
            out.append({"an": a, "luna": l, "ok": False, "mesaj": det.get("mesaj") if isinstance(det, dict) else str(det)})
    # [deficiența 312] „a doua apăsare spune iar «8 note generate»”: se numără numai notele scrise acum; lunile cu ciorna deja la zi
    # (aceleași sume) se spun separat, ca „deja generate, de validat”
    return {"luni": out, "generate": sum(1 for x in out if x["ok"] and not x.get("deja_generata")),
            "deja_generate": sum(1 for x in out if x["ok"] and x.get("deja_generata"))}


def _amortizare_suplimentara(tenant_id, an, luna, ctx):
    """[lotul 13, 517] Nota lunii (an, luna) e validată, dar unor active le lipsește amortizarea lunii: o notă ciornă separată, cu rândurile
    lor (pe activ, `amortizare_lunii.linii_lipsa`). None dacă nota lunii nu e validată (o face `tenant_amortizare`, ca până acum)."""
    from core import amortizare_lunii as _al, mf_note as _mfn, note_derivate as _nd, eticheta_nota as _et
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        with conn.cursor() as cur:
            ex = repo_contabilitate.nota_de_amortizare(cur, schema, _al.numar(an, luna))
            if not ex or _nd.ciorna_nevalidata(cur, schema, ex[0]) or _nd.respinsa(cur, schema, ex[0]):
                return None
            _uc_comun._cere_luna_deschisa(conn, schema, _uc_comun.ultima_zi_a_lunii(an, luna))
            try:
                rand = _al.linii_lipsa(cur, schema, an, luna)
            except ValueError as e:
                return {"an": an, "luna": luna, "ok": False, "mesaj": str(e)}
            if not rand:
                return {"an": an, "luna": luna, "ok": True, "deja_generata": True, "linii_nota": []}
            iid = repo_contabilitate.nota_operatiune_ciorna(
                cur, schema, _uc_comun.ultima_zi_a_lunii(an, luna),
                "Amortizare %02d/%d — %s (adăugate după nota lunii)" % (luna, an, ", ".join(d for _c, _r, d, _m in rand))[:200],
                "tablou_amortizare")[0]
            for cont_am, rata, _den, mid in rand:
                _mfn.adauga_linie(cur, schema, iid, _al.CONT_CHELTUIALA, cont_am, rata, mid)
            et = _et.nota(cur, schema, iid)
        conn.commit()
    return {"an": an, "luna": luna, "ok": True, "nota_id": iid, "nota_eticheta": et, "deja_generata": False,
            "total": round(sum(r for _c, r, _d, _m in rand), 2),  # round-ok: sumă de valori care au deja bani: curăță zgomotul float
            "linii_nota": [{"debit": _al.CONT_CHELTUIALA, "credit": c, "suma": r} for c, r, _d, _m in rand]}


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return {"istoric": _ui.istoric(conn, schema, an, luna)}


def tenant_jurnal(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            # [302, 17.10.2026] `nr_curent` e PĂSTRAT pe notă (dat la validare); ciorna n-are număr (None).
            # [14-1-1] `nr_curent` se numara de la 1 IANUARIE, nu de la inceputul lunii: norma cere
            # "numarul curent al operatiunilor inregistrate incepand de la 1 ianuarie ... pana la
            # sfarsitul exercitiului financiar". De aceea fereastra e pe AN, iar filtrul pe luna se
            # aplica DUPA numerotare - altfel fiecare luna ar reincepe de la 1.
            from decimal import Decimal
            note, tot = {}, {True: Decimal("0"), False: Decimal("0")}   # validat / ciornă
            for (iid, data, nr, desc, sursa, status, fid, dref, nrc,
                 f_tip, f_serie, f_nr, f_data,
                 deb, cre, suma, cc_id, cc_nume, p_cui, p_nume) in repo_contabilitate.jurnal_pe_an(cur, schema, f"{an}-01-01", f"{an}-{luna:02d}-01"):
                if iid not in note:
                    note[iid] = {"id": iid, "nr_curent": int(nrc) if nrc is not None else None, "data": data.isoformat(),
                                 "numar": nr, "descriere": desc, "sursa": sursa, "status": status,
                                 "sursa_eticheta": _j.eticheta_sursa(sursa, f_tip),   # [245] eticheta, nu codul; [11.1 pct.23] borderoul
                                 "factura_id": fid, "document_ref": dref,   # scris de om (editorul îl arată)
                                 "document": _j.document_justificativ(dref, f_tip, f_serie, f_nr, f_data, sursa, nr),
                                 "linii": []}
                note[iid]["linii"].append({"debit": deb, "credit": cre, "suma": float(suma),
                                           "centru_cost_id": cc_id, "centru_nume": cc_nume,
                                           "partener_cui": p_cui, "partener_nume": p_nume})   # [381]
                tot[status == "validata"] += Decimal(str(suma))
            for _nid, _st in _j.facturi_stinse(cur, schema, list(note)).items():   # [08.10, U5] chitanța: factura pe care o stinge
                note[_nid]["stinge"] = _st
            # [lotul 11, 443 — datele existente] nota scrisă înainte de 443 („Contare factura F61”) se arată cu seria separat („F6 nr. 1”),
            # derivat din factura ei; în bază rămâne cum e (nota validată nu se modifică; ciornele: core/migrare_serie_nr_descrieri.py)
            for _nid, _afisat in _j.note_fara_serie_lipita(cur, schema, list(note)).items():
                note[_nid].update(_afisat)
            # [lotul 12, C127] nota de salarii / amortizare scrisă înainte de încheierea lunii ei: semnalul pe rând
            from core import inchidere_luna as _il
            for _nid, _inainte in _il.note_contate_inainte(cur, schema, list(note)).items():
                note[_nid]["contata_inainte"] = _inainte
            # [deficiența 192, proba blocului C: „notele care vin din NIR și din raportul Z arată «Editează» și «Șterge», deși serverul
            # le refuză”] ciorna derivată dintr-un document spune ecranului ce n-o să meargă — aceeași regulă ca refuzul
            # (`jurnal_api.editeaza` / `sterge`, `note_derivate`), nu o listă a ecranului
            from core import note_derivate as _nd
            from core import drepturi as _drepturi
            # [deficiența 246] ciorna ALTUI utilizator, pentru un asistent: o vede, nu o schimbă — aceeași funcție ca refuzul din bază
            # (`ciorna_altui`, core/migrare_ciorne_proprii.py), cu utilizatorul din ctx (la o citire nu e scris pe conexiune)
            # [deficiența 258] motivul numește nota cum o arată cardul („nr. crt. 5 din 12.03.2026”, `eticheta_nota`), nu prin id
            from core import eticheta_nota as _et
            _alt = repo_contabilitate.ciorne_altui(cur, schema, [i for i, n in note.items() if n["status"] != "validata"], ctx["uid"])
            _et_alt = dict(_et.note(cur, schema, [i for i, _a in _alt]))
            for _nid, _autor in _alt:
                note[_nid]["a_altuia"] = _drepturi.ciorna_altuia(_et_alt[_nid], _autor)
            for _nid, _n in note.items():
                if _n["status"] == "ciorna":
                    _doc = _nd.documentul_sursa(cur, schema, _nid)
                    if _doc:
                        _n["derivata"] = {"fel": _doc[0], "se_sterge": _nd.se_sterge(cur, schema, _doc, _nid),
                                          "unde": _nd.mesaj_refuz(_nid, _doc)}
                    # [lotul 11, 451] ciorna depășită față de sursa ei se arată pe rând, cu refacerea — aceeași verificare ca validarea
                    from core import ciorne_depasite as _cdep
                    _dep = _cdep.verifica(conn, cur, schema, _nid)
                    if _dep:
                        _n["depasita"] = {k: _dep[k] for k in ("mesaj", "sursa", "refacere", "neregenerabila", "diferente")}
    # [14-1-1] "Sumele debitoare si sumele creditoare se totalizeaza lunar." In partida dubla fiecare
    # linie e simultan debit si credit, deci cele doua totaluri sunt egale prin constructie - se dau
    # amandoua, cum cere formularul, nu unul singur.
    lista = list(note.values())
    fara_document = sum(1 for n in lista if not n["document"])
    # [validare_note, comanda Costin 06.10.2026 pct.1] starea fiecărei note în coada de validare (la validare / respinsă,
    # cu motiv / validată) — din aceeași coadă pe care o vede cabinetul, ca jurnalul să nu spună altceva decât ea
    from core import coada_api as _coada
    with db.get_conn() as conn:
        _st = _coada.stari_note(conn, tenant_id, [n["id"] for n in lista])
    for n in lista:
        n["validare"] = _st.get(n["id"])
    # [Retest 2, pct.6] „«Total sume» include ciornele […] Totalurile registrului se fac numai pe notele validate; ciornele se arată
    # separat.” (aceeași regulă ca balanța, R36: evidența e ce a validat un om)
    return {"note": lista, "total_debit": float(round(tot[True], 2)), "total_credit": float(round(tot[True], 2)),  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            "ciorne": {"note": sum(1 for n in lista if n["status"] != "validata"), "total": float(round(tot[False], 2))},  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            "note_fara_document": fara_document}


def tenant_stat_plata(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stat-plata`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from core import stat_plata_api as _sp
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    with db.get_conn(schema) as conn:  # helper-ele (pontaj/perioada) folosesc nume necalificate -> search_path pe tenant
        # [get_safe_v1 20.08.2026] AICI se chema _snapshot_stat_plata() -> INSERT + commit pe un GET.
        # Efect: simpla deschidere a ecranului Salariati scria un rand per salariat si il comitea
        # (orice monitorizare/prefetch/al doilea tab faceau acelasi lucru), iar poarta de stergere din
        # salariati_api.sterge_salariat se inchidea din vizitare. Consumatorul (POST /calcul-cm)
        # calculeaza acum media din sursa, nu din cache-ul de navigare.
        stat = _sp.stat_final(conn, schema, an, luna)   # [validare_note] indemnizația CM cu reținerile declarate (D112)
        # [lista 5, 30.08.2026] Compozitia netului, din ACEEASI sursa ca fluturasul. Pana azi
        # componentele se vedeau numai in PDF-ul descarcat: ruta trimitea cele 12 campuri, ecranul
        # nu randa niciunul (R97). Se trimite gata compusa ca ecranul sa n-o compuna a doua oara -
        # doua liste ale aceluiasi lucru nu raman egale.
        for _r in stat:
            _r["compozitie"] = _sp.compozitie_fluturas(_r)
        with conn.cursor() as _rc:
            _reges_ok = repo_salariati.firma_are_chei_reges(_rc, tenant_id) is not None
            # [lotul 07.10 pct.15, comanda Costin 06.10.2026] „Respingerea apare pe statul de plată abia după «Contabilizează
            # statul»; se vede la deschiderea statului.” Nota lunii se găsește după numărul ei (ca în propunere), fără să
            # genereze D112: starea ei în coada de validare vine odată cu statul.
            from core import salarii_contare as _sc
            _rn = repo_contabilitate.id_nota_dupa_numar(_rc, _sc.document_ref(an, luna))
            from core import eticheta_nota as _et   # [258] nota numită ca în Registrul jurnal, nu prin id
            _rn_et = _et.nota(_rc, schema, _rn[0]) if _rn else None
    nota = None
    if _rn:
        from core import coada_api as _coada
        with db.get_conn() as conn:
            nota = {"nota_id": _rn[0], "nota_eticheta": _rn_et, "validare": _coada.stari_note(conn, tenant_id, [_rn[0]]).get(_rn[0])}
    return {"stat": stat, "reges_configurat": _reges_ok, "nota_salarii": nota}


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            r = repo_casa.cui_si_total_bon(cur, schema, bon_id)
            if not r:
                raise _erori.Inexistent("document inexistent")
            # [lotul 11, decizia Costin 10.3 pct.4, clasa „normalizare locală a CUI”] codul bonului și al facturii în forma păstrată
            # (`cui_forma.stocare`), pe ambele părți; înainte `.replace("RO", "")`, care scotea „RO” de oriunde din text
            from core import cui_forma as _forma_cui
            cui = _forma_cui.stocare(r[0]) or ""
            suma = float(r[1] or 0)
            # [lotul 12, C181, clasa 443.1] seria și numărul separat („Factura F1A nr. 3”, nu „F1A3”): `pdf_util.serie_nr`, ca peste tot
            from core.pdf_util import serie_nr as _serie_nr
            fc = [{"id": x[0], "numar": _serie_nr(x[2], x[1]),
                   "data": x[3].isoformat() if x[3] else None,
                   "total": float(x[4] or 0), "furnizor": x[5], "cui": x[6],
                   "potrivire_cui": bool(cui) and (_forma_cui.stocare(x[6]) or "") == cui,
                   "potrivire_suma": abs(float(x[4] or 0) - suma) <= 0.05} for x in repo_facturi.candidate_pentru_bon(cur, schema, cui, suma)]
    return {"facturi": fc}


def chitanta_stinge(tenant_id, bon_id, c, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/bonuri/{bon_id}/stinge`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            r = repo_casa.tip_si_status_bon(cur, schema, bon_id)
            if not r:
                raise _erori.Inexistent("document inexistent")
            if (r[0] or "bon") != "chitanta":
                raise _erori.CerereGresita("documentul nu e chitanta")
            if r[1] != "de_verificat":
                raise _erori.CerereGresita("documentul nu e în așteptare")
        rez = casa_api.adauga(conn, schema, {"data": c.data, "categorie": "plata_furnizor",
                                             "suma": c.suma, "document": c.document or ("CHIT-%d" % bon_id),
                                             "fel_document": "chitanța furnizorului", "avans_automat": False,
                                             "partener": c.partener, "cui": c.cui,
                                             # [lotul 6 pct.3a, 278] nota plății stinge factura (`inregistrari.factura_id`)
                                             "facturi": casa_api.alocare_pe_factura(conn, schema, "plata_furnizor", c.factura_id, c.suma)})
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
    # [lotul 11, deficiența 440] suma, data și cota se verifică toate, fiecare lângă câmpul ei din „Chitanță fără factură” (`ch-…`);
    # metoda AMEF nedeclarată în Date firmă (starea firmei) rămâne refuzul unic, cu trimiterea spre ecran
    er = _erori.ErorileFormularului("Chitanța nu s-a emis")
    _amef_e = None
    if c.suma <= 0:
        er.camp("ch-suma", "suma trebuie să fie > 0")
    client_nume = client_cui = reprezentand = None
    total_fact = None
    cota = linii = None
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if not c.factura_id:
                # [D394 Î2, 03.10.2026] fără factură: cu cotă = VÂNZARE (numai la firma exceptată de la AMEF), fără
                # cotă = încasare de creanță (5311=4111, ca până azi); la firma exceptată cota e obligatorie — o
                # încasare neclasificată n-ar avea unde intra în D394 (decizia Costin: refuz numit, nu zero).
                from core import activitati_amef as _amef
                exceptata, cont_venit = (repo_firma_profil.amef_si_cont_venit(cur, schema)
                                          or (None, _fp.CONT_VENIT_IMPLICIT_DEFAULT))
                import datetime as _dt
                if exceptata is None:   # [lotul 07.10 B] neales în Date firmă: se cere acum, o dată (starea firmei: refuz unic)
                    raise _erori.CerereGresita(_amef.detaliu(_amef.refuz_nedeclarata()))
                _dc = None
                try:
                    _dc = _dt.date.fromisoformat(str(c.data)[:10])
                except ValueError:
                    er.camp("ch-data", "Data chitanței: %r nu e o dată din calendar. Se așteaptă forma AAAA-LL-ZZ." % (c.data,))
                try:
                    if not exceptata and c.cota_tva is not None:
                        raise _amef.refuz_vanzare_neexceptata()
                    if exceptata and c.cota_tva is None:
                        raise _amef.refuz_cota_lipsa()
                    if exceptata and _dc is not None:
                        _permise = _amef.cote_permise(_dc)
                        if c.cota_tva not in _permise:
                            raise _amef.refuz_cota_nepermisa("%g" % c.cota_tva, _permise)
                except ValueError as e:
                    _amef_e = e
                    er.camp("ch-cota", str(e))
            if er:
                # o singură problemă, a cotei: refuzul ei întreg, ca înainte (`activitati_amef.detaliu`, cu codul și ecranul)
                raise _erori.CerereGresita(_amef.detaliu(_amef_e) if (_amef_e is not None and len(er.campuri) == 1)
                                           else er.detaliu())
            if not c.factura_id and exceptata:
                cota = int(c.cota_tva)
                baza, tva = _amef.defalcare(c.suma, cota)
                linii = [("5311", cont_venit, baza), ("5311", "4427", tva)]
                client_nume = (c.client_nume or "").strip() or None
                reprezentand = (c.reprezentand or "").strip() or None
            if c.factura_id:
                r = repo_facturi.factura_pentru_chitanta(cur, schema, c.factura_id)
                if not r:
                    raise _erori.Inexistent("factură inexistentă")
                if r[5] != "emisa":
                    raise _erori.CerereGresita("chitanta se emite doar pentru facturi emise")
                client_nume, client_cui, total_fact = r[2], r[3], float(r[4] or 0)
                # [lotul 11, 443] seria și numărul separat („factura F6 nr. 1”, nu „F61”): `pdf_util.serie_nr` taie și seria din numărul emis
                from core.pdf_util import serie_nr as _serie_nr
                reprezentand = "contravaloare factura %s din %s" % (_serie_nr(r[0], r[1]), data_ro(r[6]))
            serie = chitanta_serie_sau_refuz(cur, schema)
            nr = repo_casa.urmatorul_numar_chitanta(cur, schema, serie)[0]
        rez = casa_api.adauga(conn, schema, {"data": c.data,
                                             "categorie": "vanzare_fara_factura" if linii else "incasare_client",
                                             "suma": c.suma, "document": "%s-%s" % (serie, nr), "fel_document": "chitanța",
                                             "stinge": reprezentand,   # [retest 08.10 pct.19] „… și factura stinsă”
                                             "partener": client_nume, "cui": client_cui,
                                             # [lotul 6 pct.3a, 278] nota chitanței stinge factura (`inregistrari.factura_id`)
                                             "facturi": casa_api.alocare_pe_factura(conn, schema, "incasare_client", c.factura_id, c.suma)},
                              linii=linii)
        if rez.get("eroare"):
            raise _erori.CerereGresita(rez["eroare"])
        with conn.cursor() as cur:
            cid = chitanta_scrie(cur, schema, serie, nr, c.data, c.factura_id, client_nume, client_cui, c.suma, reprezentand, rez["id"],
                                 rez["inregistrare_id"], cota, total_fact)
    return {"ok": True, "chitanta_id": cid, "serie": serie, "numar": nr, "nota": rez.get("nota"),
            "avertismente": rez.get("avertismente") or []}


def chitanta_serie_sau_refuz(cur, schema, prefix=""):
    """Seria chitanțelor firmei (Date firmă), sau refuzul numit cu trimitere la câmpul ei. [decizia Costin 07.10, pct.5] cerută la prima
    folosire, ca seria facturii; nu „CH” din oficiu. Un singur loc: „Emite chitanță” și încasarea facturii din Casă (456)."""
    rs = repo_firma_profil.seria_chitantei(cur, schema)
    serie = str((rs[0] if rs else None) or "").strip()
    if not serie:
        raise _erori.CerereGresita(_uc_comun.refuz_spre_ecran(prefix + MESAJ_SERIE_CHITANTA_LIPSA, COD_SERIE_CHITANTA_LIPSA,
                                                               "date_firma", "OMFP 2634/2015 anexa 1 pct.24"))
    return serie


def chitanta_scrie(cur, schema, serie, nr, data, factura_id, client_nume, client_cui, suma, reprezentand, op_id, nota_id, cota=None,
                   total_fact=None):
    """Chitanța emisă pe operațiunea de casă `op_id` (nota `nota_id`); factura plătită integral devine încasată. Un singur loc:
    „Emite chitanță” și încasarea facturii din Casă (456). Întoarce id-ul chitanței."""
    cid = repo_casa.adauga_chitanta(cur, schema, serie, nr, data, factura_id, client_nume, client_cui, suma, reprezentand, op_id,
                                    nota_id, cota)[0]
    if factura_id and total_fact is not None and float(suma) >= float(total_fact) - 0.005:
        repo_facturi.marcheaza_platita(cur, schema, factura_id)
    return cid


#: [lotul 11, deficiența 456] prefixul refuzului seriei, când încasarea unei facturi din Casă cere chitanța
PREFIX_INCASARE_FARA_SERIE = ("Încasarea nu s-a salvat: încasarea în numerar a facturii se face cu chitanță (OMFP 2634/2015, cod 14-4-1), "
                              "emisă de aplicație. ")
#: [lotul 12, 456 decizia (a)] la fel, când încasarea de la client e fără factură (avansul)
PREFIX_AVANS_FARA_SERIE = ("Încasarea nu s-a salvat: încasarea în numerar de la client se face cu chitanță (OMFP 2634/2015, cod 14-4-1), "
                           "emisă de aplicație. ")


def chitante_pe_incasare(cur, schema, serie, rez, op=None):
    """[lotul 11, deficiența 456] „încasarea în numerar de la o firmă se salvează fără chitanță. Emite automat chitanța, cu seria firmei
    și PDF.” Fiecare operațiune a dispoziției care încasează o factură emisă primește chitanța ei: seria firmei, numărul următor, clientul
    și „contravaloare factura … din …” de pe factură (ca „Emite chitanță”), legată de operațiune și de notă; documentul operațiunii
    nescris de contabil devine numărul chitanței. [lotul 12, decizia Costin 456 (a), verbatim în DECIZII: „chitanța se emite și pentru
    încasarea în numerar fără factură (avansul)”] Partea fără factură (avansul de la client, încasarea nelegată) primește și ea chitanța,
    cu clientul din dispoziție (`op`) și „avans de la client” (sau ce a scris contabilul la „stinge”). Fără cotă: la firma neexceptată de
    la AMEF e încasare (5311 = 4111); la cea exceptată D394 o numește „de clasificat” până primește cota (`d394._op2_din_chitante`).
    Temei: OMFP 2634/2015 anexa 2, Chitanța (cod 14-4-1): „Chitanța și chitanța pentru operațiuni în valută sunt documente justificative
    de înregistrare în registrul de casă/registrul de casă în valută și în contabilitate a încasărilor și plăților efectuate în numerar
    [...] Se întocmește pentru fiecare sumă încasată, de către casierul entității și se semnează de acesta pentru primirea sumei.”"""
    from core.pdf_util import serie_nr as _serie_nr
    from core import casa_api
    out = []
    op = op or {}
    for o in rez.get("operatiuni") or []:
        nr = repo_casa.urmatorul_numar_chitanta(cur, schema, serie)[0]
        data_op, doc = repo_casa.data_si_documentul_operatiunii(cur, schema, o["id"])
        if o.get("factura_id"):
            r = repo_facturi.factura_pentru_chitanta(cur, schema, o["factura_id"])
            cid = chitanta_scrie(cur, schema, serie, nr, data_op, o["factura_id"], r[2], r[3], o["suma"],
                                 "contravaloare factura %s din %s" % (_serie_nr(r[0], r[1]), data_ro(r[6])), o["id"],
                                 o["inregistrare_id"], None, float(r[4] or 0))
        else:   # [lotul 12, 456 (a)] încasarea fără factură: clientul din dispoziție, „avans de la client” dacă e avans
            cid = chitanta_scrie(cur, schema, serie, nr, data_op, None, (str(op.get("partener") or "").strip() or None),
                                 (str(op.get("cui") or "").strip() or None), o["suma"],
                                 "avans de la client" if o.get("avans") else (str(op.get("stinge") or "").strip() or "încasare de la client"),
                                 o["id"], o["inregistrare_id"])
        if not str(doc or "").strip():
            repo_casa.documentul_chitantei(cur, schema, o["id"], o["inregistrare_id"], "%s-%s" % (serie, nr))
        # [lotul 12, deficiența 168] nota s-a scris înaintea chitanței: descrierea ei o numește acum, cu factura stinsă
        casa_api.nota_numeste_chitanta(cur, schema, o["id"], "%s-%s" % (serie, nr))
        out.append({"chitanta_id": cid, "serie": serie, "numar": nr, "factura_id": o["factura_id"], "operatiune_id": o["id"]})
    return out


def chitanta_cota(tenant_id, chitanta_id, c, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/chitante/{chitanta_id}/cota`; docstringul ei a ramas in
    stratul HTTP. [D394 Î2] Chitanța fără factură și fără cotă a firmei exceptate devine vânzare."""
    from core import activitati_amef as _amef
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = repo_casa.chitanta_de_clasificat(cur, schema, chitanta_id)
            if not r:
                raise _erori.Inexistent("chitanță inexistentă")
            _id, data_, suma, factura_id, cota_veche, anulata, op_id, iid, status = r
            exceptata, cont_venit = (repo_firma_profil.amef_si_cont_venit(cur, schema)
                                          or (None, _fp.CONT_VENIT_IMPLICIT_DEFAULT))
            try:
                if exceptata is None:   # [lotul 07.10 B] neales în Date firmă: se cere acum, o dată
                    raise _amef.refuz_nedeclarata()
                if not exceptata:
                    raise _amef.refuz_vanzare_neexceptata()
                if factura_id or anulata or cota_veche is not None:
                    raise _amef.refuz_clasificare(
                        "chitanța e a unei facturi." if factura_id else "chitanța e anulată." if anulata
                        else "chitanța are deja cota %g%%." % cota_veche)
                if not iid or status != "ciorna":
                    raise _amef.refuz_clasificare(
                        "nota chitanței e validată — anulează întâi validarea notei, apoi stabilește cota.")
                if c.cota_tva is None:
                    raise _amef.refuz_cota_lipsa()
                _permise = _amef.cote_permise(data_)
                if c.cota_tva not in _permise:
                    raise _amef.refuz_cota_nepermisa("%g" % c.cota_tva, _permise)
            except ValueError as e:
                raise _erori.CerereGresita(_amef.detaliu(e))
        _uc_comun._cere_luna_deschisa(conn, schema, data_)
        cota = int(c.cota_tva)
        baza, tva = _amef.defalcare(suma, cota)
        linii = [("5311", cont_venit, baza), ("5311", "4427", tva)]
        with conn.cursor() as cur:
            repo_casa.clasifica_vanzare(cur, schema, chitanta_id, cota, iid, op_id, linii)
    return {"ok": True, "chitanta_id": chitanta_id, "cota_tva": cota,
            "nota": " + ".join("%s=%s" % (d, k) for d, k, v in linii if v)}


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    with db.get_conn(schema) as conn:  # balanta foloseste nume necalificate -> search_path pe tenant
        randuri = documente_api.balanta(conn, schema, an, luna)
        note_lunii = documente_api.note_lunii(conn, schema, an, luna)
        ciorne = documente_api.ciorne_balanta(conn, schema, an, luna)   # [08.10 §6 pct.7, R36] separat, cu indicator
        av = documente_api.avertisment_balanta(conn, schema, an)   # [lotul 10, 425] rulajele dinainte de preluare lipsesc
    return {"randuri": randuri, "note_lunii": note_lunii, "ciorne": ciorne,
            "avertismente": [av] if av else [],
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        if varianta == "venituri_pf":
            return _ref.registru_pf(conn, schema, an)
    # [lotul 6, găsit de garda 285 (toate cardurile firmei): 500 „relation firma_profil does not exist”] varianta PROFIT trece prin
    # `d101.genereaza`, care citește tabelele firmei fără schemă în nume: cere conexiunea FIRMEI (`get_conn(schema)`), nu pe cea publică
    # (care își resetează `search_path`). Refuzul generatorului (date de firmă lipsă) e al datelor, nu o cădere: 422, ca la S1005.
    with db.get_conn(schema) as conn:
        try:
            return _ref.registru_profit(conn, schema, an, totalizare)
        except _ref.RegistruNeconstruibil:   # întâi: e și ea un ValueError
            # 409, nu 400: cererea e legitimă, iar refuzul nu e al ei — e al nostru, și poartă de ce.
            # Corpul e o AFIRMAȚIE tipată, nu un dicționar de proză (decizia din 21.08): e o
            # afirmație despre datele firmei, iar `verificare_rupta` o ține să nu fie citită ca un
            # verdict gri permanent — „nu se poate pe trimestru", nu „nu există pe trimestru".
            raise _erori.Conflict(_ref.refuz_totalizare(an, totalizare))
        except ValueError as e:
            raise _erori.DateInvalide(str(e))


def _schema_firmei(conn, tenant_id, ctx):
    schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    return schema


def ajustari_fiscale_lista(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `GET /tenants/{tenant_id}/ajustari-fiscale` (deficiența 378)."""
    _uc_comun._cere_perioada(an=an)
    from core import ajustari_fiscale as _aj
    with db.get_conn() as conn:
        schema = _schema_firmei(conn, tenant_id, ctx)
        with conn.cursor() as cur:
            ajustari = _aj.lista(cur, schema, an)
        # [378, lotul 9] rândurile care se iau din conturi, pe anul întreg (notele validate), ca omul să vadă cifra înainte de D100 / D101
        # [lotul 10, deficiența 425] aceeași bază ca generatorul D101 (`d101.rulaje_fereastra`: note + rulajele preluate)
        import datetime as _dt
        from core import d101 as _d101
        with conn.cursor(cursor_factory=_E_sol.RealDictCursor) as cur:
            repo_contabilitate.search_path_firma(cur, schema)
            rulaje = _d101.rulaje_fereastra(cur, schema, _dt.date(int(an), 1, 1), _dt.date(int(an) + 1, 1, 1))
        scrise = {a["rand"] for a in ajustari}
        din_conturi = [{"rand": k, "eticheta": _aj.RANDURI[k][0], "sursa": _aj.DIN_CONTURI[k][1], "suma": str(v),
                        "inlocuit": k in scrise} for k, v in _aj.din_conturi(rulaje).items()]
    return {"an": an, "ajustari": ajustari, "anuale": list(_aj.ANUALE), "din_conturi": din_conturi,
            "randuri": [{"rand": k, "eticheta": v[0], "grupa": v[1]} for k, v in _aj.RANDURI.items()]}


def ajustari_fiscale_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `POST /tenants/{tenant_id}/ajustari-fiscale` (deficiența 378)."""
    from core import ajustari_fiscale as _aj
    trim = corp.get("trim")
    trim = int(trim) if str(trim or "").strip().isdigit() else None
    motiv = _aj.valideaza(corp.get("an"), trim, corp.get("rand"), corp.get("suma"))
    if motiv:
        raise _erori.DateInvalide(motiv)
    with db.get_conn() as conn:
        schema = _schema_firmei(conn, tenant_id, ctx)
        with conn.cursor() as cur:
            aid = _aj.adauga(cur, schema, corp.get("an"), trim, corp.get("rand"), corp.get("suma"), (corp.get("descriere") or "").strip(),
                             (corp.get("document") or "").strip(), ctx.get("uid"))
        conn.commit()
    return {"ok": True, "id": aid}


def ajustari_fiscale_sterge(tenant_id, ajustare_id, ctx):
    """[P7 · use-case] Corpul rutei `DELETE /tenants/{tenant_id}/ajustari-fiscale/{ajustare_id}` (deficiența 378)."""
    from core import ajustari_fiscale as _aj
    with db.get_conn() as conn:
        schema = _schema_firmei(conn, tenant_id, ctx)
        with conn.cursor() as cur:
            if not _aj.sterge(cur, schema, ajustare_id):
                raise _erori.Inexistent("Ajustarea nu mai există (a fost ștearsă între timp).")
        conn.commit()
    return {"ok": True}


def registru_fiscal_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-evidenta-fiscala`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_evidenta_fiscala as _ref
    an = corp.get("an")
    if not an:
        raise _erori.CerereGresita({
                "mesaj": "Rândul nu s-a înscris: lipsește anul.",
                "erori_campuri": [{"camp": "an", "mesaj": "Scrie anul rândului."}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            return _ref.adauga_pf(conn, schema, int(an), corp)
        except _ref.InregistrareIncompletaPF as e:
            raise _erori.CerereGresita({
                    "mesaj": "Rândul nu s-a înscris: registrul cere un câmp care lipsește din cerere.",
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _ri.registru(conn, schema, exercitiu, momentul)


def registru_inventar_propunere(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registru-inventar/propunere`; docstringul ei a ramas in stratul HTTP."""
    from core import registru_inventar as _ri
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                "mesaj": "Rândul nu s-a înscris: lipsește exercițiul financiar.",
                "erori_campuri": [{"camp": "exercitiu", "mesaj": "Scrie exercițiul financiar (anul)."}]})
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            return _ri.adauga(conn, schema, int(exercitiu), corp)
        except _chei.CheieDublata as e:   # [lotul 10, C73 / U2] numărul curent nealocat după cursele reluate -> 409 numit, nu 500
            raise _erori.Conflict(e.detaliu())
        except _ri.InregistrareIncompleta as e:
            raise _erori.CerereGresita({
                    "mesaj": "Rândul nu s-a înscris: registrul cere un câmp care lipsește din cerere.",
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _r.registru(conn, schema, fel, an)


def registre_art321_adauga(tenant_id, fel, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registre-art321/{fel}`; docstringul ei a ramas in stratul HTTP."""
    from core import registre_art321 as _r
    if fel not in _r.FELURI:
        raise _erori.Inexistent("registru necunoscut: %r" % fel)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            return _r.adauga(conn, schema, fel, corp)
        except _chei.CheieDublata as e:   # [lotul 10, C73 / U2] numărul de ordine nealocat după cursele reluate -> 409 numit, nu 500
            raise _erori.Conflict(e.detaliu())
        except _r.InregistrareIncompleta as e:
            # Mesajul de pe CAMP e scurt — el se randeaza langa un input, iar acolo un paragraf de
            # normа nu se citeste. Norma intreaga sta la nivelul refuzului, unde are loc.
            raise _erori.CerereGresita({
                    "mesaj": "Rândul nu s-a înscris: registrul cere un câmp care lipsește din cerere.",
                    "erori_campuri": [{"camp": e.camp, "mesaj": "Completează câmpul cu o valoare validă: registrul o cere."}],
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
            raise _erori.DateInvalide("Adresa magazinului nu e o adresă web: %r. Se așteaptă ceva "
                                         "de forma https://magazin.ro." % _u)
    _campuri = [k for k in ("url", "ck", "cs") if k in (corp or {})]
    if not _campuri:
        raise _erori.DateInvalide("N-ai trimis niciun câmp. Cererea asta ar fi golit adresa "
                                     "magazinului și cheile lui, adică ar fi oprit canalul "
                                     "WooCommerce — dacă asta vrei, trimite explicit adresa și cheile "
                                     "goale.")
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
        email = _uc_comun._email_client_tenant(conn, tenant_id)
        # [deficiența 320] „mesaj_cabinet”: clienții din portal primesc notificarea, pe canalul ales; emailul direct rămâne pentru adresa
        # firmei care nu e (încă) a unui client cu alegerile salvate. În ACEEAȘI tranzacție cu răspunsul: răspunsul și anunțul lui
        # se scriu împreună sau deloc
        if _uc_comun._notifica_clientii(conn, tenant_id, "mesaj_cabinet", "Cabinetul ți-a scris în Solicitări.", email_direct=email):
            email = None
        conn.commit()
        if email:
            nume = _uc_comun._nume_tenant(conn, tenant_id)
            subiect = "Răspuns nou de la contabilul tău"
            html = ("<div style='font-family:sans-serif;font-size:15px;color:#111'>"
                    "<p>Bună,</p><p>Contabilul tău ți-a răspuns la o solicitare pentru <b>" +
                    _common.esc(nume or "firma ta") + "</b>:</p>"
                    "<p style='background:#f5f5f5;padding:14px;border-radius:8px'>" +
                    _common.esc(date.mesaj).replace("\r", "").replace("\n", "<br>") + "</p>"
                    "<p><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
                    "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>"
                    "Deschide portalul</a></p></div>")
            _de_trimis = (email, subiect, html)
    # [P5 val 3, 11.09.2026] AICI, nu inauntru. `conn.commit()` s-a facut mai sus, deci raspunsul e
    # deja in evidenta; apelul la Brevo (termen 15 s) nu mai tine nimic din pool. Se trimite exact
    # cand exista adresa clientului, ca inainte.
    if _de_trimis is not None:
        _obs.trimite_email_html_sau_semnaleaza("email raspuns client", *_de_trimis)
    return {"ok": True}


#: Stările unei linii de extras, așa cum le scrie `reconciliere_api` (05.10.2026: filtrul cerea „noua/potrivita/…”, baza
#: scrie „nou/potrivit/…”, deci orice filtru întorcea o listă goală).
STARI_EXTRAS = ("nou", "potrivit", "contat", "ignorat")


def banca_rec_lista(tenant_id, status, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere`; docstringul ei a ramas in stratul HTTP."""
    if status is not None and status not in STARI_EXTRAS:
        raise _erori.DateInvalide("stare necunoscută: %r (stările reconcilierii: %s)"
                                     % (status, ", ".join(STARI_EXTRAS)))
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return {"linii": _rec.lista(conn, schema, status)}


def banca_rec_conteaza(tenant_id, linie_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/{linie_id}/conteaza`; docstringul ei a ramas in stratul HTTP."""
    from core import reconciliere_api as _rec
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _rec.conteaza(conn, schema, linie_id, corp.get("alocari"))
        if rez and not rez.get("eroare"):
            from core import eticheta_nota as _et   # [258] notele create, numite ca în Registrul jurnal (nu prin id)
            with conn.cursor() as _c:
                _et.in_raspuns(_c, schema, rez)
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _rc.fisa_partener(conn, schema, cui, de, pana)


def rapoarte_salvate_lista(tenant_id, tip_raport, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-salvate`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return {"variante": _rc.variante(conn, schema, tip_raport)}


def rapoarte_salvate_creeaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rapoarte-salvate`; docstringul ei a ramas in stratul HTTP."""
    from core import rapoarte_comerciale_api as _rc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _reg.lista(conn, schema, an)


def registratura_creeaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/registratura`; docstringul ei a ramas in stratul HTTP."""
    _d = (corp.get("data") or "").strip()
    if _d:
        from datetime import date as _date_reg
        try:
            _zi = _date_reg.fromisoformat(_d)
        except ValueError:
            _m = "Data înregistrării nu e o dată: %r (se așteaptă AAAA-LL-ZZ)." % _d
            raise _erori.DateInvalide({"mesaj": _m, "erori_campuri": [{"camp": "rg-data", "mesaj": _m}]})   # [440] lângă câmp
        _uc_comun._cere_perioada(an=_zi.year)
    from core import registratura_api as _reg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            rez = _reg.inregistreaza(conn, schema, corp, ctx["uid"])
        except _chei.CheieDublata as e:   # [lotul 10, C73 / U2] numărul nealocat după cursele reluate -> 409 numit, nu 500
            raise _erori.Conflict(e.detaliu())
    if not rez.get("ok"):
        # [440] fiecare refuz lângă câmpul lui din Registratură (`rg-dir`, `rg-desc`); toate deodată, când `inregistreaza` le întoarce pe
        # toate (`coduri`), altfel codul unic de până acum
        campuri = {"DIRECTIE_INVALIDA": ("rg-dir", "Alege direcția înregistrării: intrare sau ieșire."),
                   "DESCRIERE_GOALA": ("rg-desc", "Scrie descrierea documentului înregistrat.")}
        er = _erori.ErorileFormularului("Înregistrarea nu s-a făcut")
        for _cod in rez.get("coduri") or [rez.get("cod")]:
            if _cod in campuri:
                er.camp(*campuri[_cod])
            else:
                er.fara_camp("eroare")
        er.refuza()
    return rez


def contracte_sabloane_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return {"sabloane": _ct.lista_sabloane(conn, schema)}


def contracte_sabloane_salveaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _ct.salveaza_sablon(conn, schema, corp.get("id"), corp.get("nume"),
                                  corp.get("continut"), ctx["uid"])
    if not rez.get("ok"):
        if rez.get("erori_campuri"):   # [440] numele, textul și marcajele, toate deodată, fiecare lângă câmpul ei
            raise _erori.DateInvalide({"mesaj": rez["mesaj"], "erori_campuri": rez["erori_campuri"]})
        if rez.get("cod") == "NUME_EXISTA":
            _m = "Există deja un șablon cu numele ăsta. Alege alt nume, sau editează-l pe cel existent."
            raise _erori.DateInvalide({"mesaj": _m, "erori_campuri": [{"camp": "c-nume", "mesaj": _m}]})
        raise _erori.DateInvalide("sablon inexistent" if rez.get("cod") == "INEXISTENT" else "eroare")
    return rez


def contracte_sabloane_sterge(tenant_id, sid, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/sabloane/{sid}`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [lotul 13, 536] lista întreagă (ecranul Centre de cost) poartă și ce are azi fiecare centru: salariații și mijloacele fixe
        return {"centre": _cc.lista(conn, schema, doar_active=doar_active), **({} if doar_active else {"alocari": _cc.alocari(conn, schema)})}


def centre_cost_alocari(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/alocari` (lotul 13, deficiența 536): centrul de cost al salariaților și
    al mijloacelor fixe și al articolelor de stoc (536 / NIR, decizia Costin (a)), `{salariati: {id: centru | null}, mijloace: {…},
    articole: {…}}`. Centrul inactiv / inexistent se refuză lângă
    rândul lui; notele deja scrise nu se schimbă."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            sal = {int(k): v for k, v in dict(corp.get("salariati") or {}).items()}
            mf = {int(k): v for k, v in dict(corp.get("mijloace") or {}).items()}
            art = {int(k): v for k, v in dict(corp.get("articole") or {}).items()}   # [536 / NIR, decizia (a)] articolele de stoc
        except (TypeError, ValueError):
            raise _erori.DateInvalide("Alocarea nu s-a salvat: salariații, mijloacele fixe și articolele se trimit după numărul lor din listă.")
        r = _cc.seteaza_alocari(conn, schema, sal, mf, art)
        if r.get("eroare"):
            raise _erori.DateInvalide({"mesaj": r["eroare"], "erori_campuri": r["erori_campuri"]})
        return r   # `get_conn` comite la ieșire (ca la celelalte rute ale centrelor)


def centre_cost_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost`; docstringul ei a ramas in stratul HTTP."""
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            activ = _uc_comun.bifa(corp, "activ", True)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        r = _cc.seteaza_activ(conn, schema, centru_id, activ)
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _cc.raport_realizat(conn, schema, de, pana)


def centre_cost_varianta(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/centre-cost/varianta`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import centre_cost_api as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
    from core import drepturi as _drepturi
    with db.get_conn() as conn:
        schema = _uc_comun._rip_ctx(conn, ctx, tenant_id)
        reg = _r.lista(conn, schema, an, luna, status)
        # [deficiența 246] ciorna altui utilizator, pentru un asistent: o vede, n-o șterge — aceeași regulă ca refuzul din bază
        alt = dict(_r.ciorne_altui(conn, schema, [o["id"] for o in reg["operatiuni"] if o["status"] == "ciorna"], ctx["uid"]))
        from core import eticheta_nota as _et   # [deficiența 258] operațiunea cum o arată rândul ei, nu prin id
        with conn.cursor() as cur:
            for o in reg["operatiuni"]:
                if o["id"] in alt:
                    o["a_altuia"] = _drepturi.ciorna_altuia(_et.rip(cur, schema, o["id"]), alt[o["id"]], rip=True)
        return reg


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        reg = _c.registru(conn, schema, an, luna)
        # [deficiența 279] starea REALĂ a notei pe rând: ciornă / la validare în cabinet / respinsă / validată. O notă la validare nu
        # se șterge și nu se leagă (serverul refuză) — ecranul nu le mai oferă.
        from core import coada_api as _coada
        st = _coada.stari_note(conn, tenant_id, [o["inregistrare_id"] for o in reg["operatiuni"] if o.get("inregistrare_id")])
        for o in reg["operatiuni"]:
            v = st.get(o.get("inregistrare_id")) or {}
            o["stare_coada"], o["motiv_respingere"] = v.get("stare_coada"), v.get("motiv_respingere")
            if o["stare_coada"] == "la_senior":
                o["se_leaga"] = False
        return reg


def casa_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/casa/operatiuni`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [lotul 11, deficiența 456] încasarea unei facturi în numerar se face cu chitanță: seria firmei se cere ÎNAINTE de orice scriere
        # (refuz numit, cu „Deschide Date firmă”), iar chitanța se emite în aceeași tranzacție cu operațiunea (`chitante_pe_incasare`)
        # [lotul 12, 456 (a)] și încasarea fără factură (avansul de la client): orice încasare de la client din Casă are chitanța ei
        serie = None
        if (corp or {}).get("categorie") == "incasare_client":
            with conn.cursor() as cur:
                serie = chitanta_serie_sau_refuz(cur, schema, PREFIX_INCASARE_FARA_SERIE if (corp or {}).get("facturi")
                                                 else PREFIX_AVANS_FARA_SERIE)
        rez = _c.adauga(conn, schema, corp)
        if serie and not rez.get("eroare"):
            with conn.cursor() as cur:
                rez["chitante"] = chitante_pe_incasare(cur, schema, serie, rez, corp)
    if rez.get("eroare"):
        # [lotul 11, deficiența 440] toate erorile dispoziției, fiecare lângă câmpul ei din formularul Casă (`erori_campuri`); înainte se
        # trimitea numai textul, iar `c-avans-dest` se pierdea
        if rez.get("erori_campuri"):
            raise _erori.CerereGresita({"mesaj": rez["eroare"], "erori_campuri": rez["erori_campuri"], "cod": rez.get("cod")})
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def casa_sterge(tenant_id, op_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/casa/operatiuni/{op_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _c.sterge(conn, schema, op_id)
    if rez is None:
        raise _erori.Inexistent("operațiune inexistentă")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def casa_previzualizare(tenant_id, corp, ctx):
    """[lotul 6 pct.3, 278] `casa_api.previzualizare` — nimic scris."""
    from core import casa_api as _c
    import datetime as _dt
    try:
        _dt.date.fromisoformat(str((corp or {}).get("data") or "")[:10])
    except ValueError:
        raise _erori.CerereGresita("Data dispoziției lipsește sau nu e o dată din calendar.")
    with db.get_conn() as conn:
        # poarta firmelor ACTIVE (nu cea de citire istorică, R84): previzualizarea pregătește o scriere
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _uc_comun._raspuns(_c.previzualizare(conn, schema, corp or {}))


def casa_leaga(tenant_id, op_id, corp, ctx):
    """[lotul 6 pct.3a, 278] `casa_api.leaga`: nota operațiunii (ciornă) primește factura pe care o stinge."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _c.leaga(conn, schema, op_id, (corp or {}).get("factura_id"))
    if rez is None:
        raise _erori.Inexistent("operațiune inexistentă")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def casa_storneaza(tenant_id, op_id, corp, ctx):
    """[Retest 2, pct.4] Stornarea operațiunii de casă cu notă validată (`casa_api.storneaza`); data = cea dată, în luna deschisă."""
    from core import casa_api as _c
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        data = (corp or {}).get("data")
        _uc_comun._cere_luna_deschisa(conn, schema, data)
        rez = _c.storneaza(conn, schema, op_id, data)
    if rez is None:
        raise _erori.Inexistent("operațiune inexistentă")
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return {"ok": True, **rez}


def stocuri_lista(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/nir`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)   # [lotul 5] `luna=13` dadea `500`, `an=1900` dadea `200 {"nir": []}`
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        nirs = _s.lista_nir(conn, schema, an, luna)
        # [retest 07.10 R1] NIR-ul respins rămâne în listă, marcat, cu motivul (și NIR-ul care l-a refăcut)
        from core import coada_api as _coada
        toate = [i for n in nirs for i in _s.note_nir(n)]
        stari = _coada.stari_note(conn, tenant_id, toate)
        return {"nir": _s.stare_validare_nir(nirs, stari, _s.refaceri_nir(conn, schema, [n["id"] for n in nirs]))}


def stocuri_adauga(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/nir`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [lotul 11, decizia Costin 10.3 pct.4, verbatim] „NIR cu număr repetat: refuzat, cu mesaj numit.” NIR-urile firmei se scriu unul
        # după altul (lacăt pe tranzacție), iar numărul deja dat altui NIR în același an se refuză lângă „număr NIR”, ÎMPREUNĂ cu celelalte
        # refuzuri ale NIR-ului (440: toate deodată) — NIR-ul se verifică sub un savepoint și nu se scrie nimic.
        with conn.cursor() as _c:
            repo_stocuri.blocheaza_nir_urile(_c, schema)
            _dubla = _nir_cu_numarul(_c, schema, corp.get("numar"), corp.get("data"), corp.get("refacut_din_id"))
            if _dubla:
                repo_stocuri.savepoint_nir_numar_repetat(_c)
        rez = _s.adauga_nir(conn, schema, corp, cere_decizia=True)   # [399] decizia omului (factura sosită, cota transportului)
        if _dubla:
            with conn.cursor() as _c:
                repo_stocuri.inapoi_la_nir_numar_repetat(_c)
            _msg = ("Numărul %s e deja al NIR-ului din %s (%s). Scrie alt număr; un NIR respins la validare se reface din lista NIR-urilor "
                    "(„Refă NIR-ul”), cu numărul lui." % (_dubla[0], data_ro(_dubla[1]), _dubla[2] or "furnizor fără nume"))
            _alte = (rez.get("erori_campuri") or []) if rez.get("eroare") else []
            rez = {"eroare": "NIR-ul nu s-a salvat: numărul unui NIR nu se dă de două ori în același an." + (
                " " + rez["eroare"] if rez.get("eroare") else ""), "cod": COD_NIR_NUMAR_REPETAT,
                "erori_campuri": [{"camp": "sn-numar", "mesaj": _msg}] + [x for x in _alte if x.get("camp") != "sn-numar"]}
        if rez.get("cod") == "NESCHIMBATA":   # [S3] NIR-ul refăcut identic cu cel respins: confirmare, nimic scris
            conn.rollback()
            return rez
    if rez.get("eroare"):
        if rez.get("ecran"):   # [lotul 07.10 B, C10] metoda de stoc nedeclarată: refuzul trimite în Date firmă (butonul spre ecran)
            raise _erori.CerereGresita(_uc_comun.refuz_spre_ecran(rez["eroare"], rez.get("cod"), rez["ecran"], None))
        _ec = rez.get("erori_campuri")  # [cap.24] contract {mesaj, erori_campuri} ca celelalte ecrane
        raise _erori.DateInvalide({"mesaj": rez["eroare"], "erori_campuri": _ec} if _ec else rez["eroare"])
    return rez


#: [lotul 11, decizia 10.3] NIR-ul cu numărul deja dat altui NIR în același an
COD_NIR_NUMAR_REPETAT = "NIR_NUMAR_REPETAT"


def _nir_cu_numarul(cur, schema, numar, data, refacut_din_id=None):
    """[decizia 10.3] NIR-ul care poartă deja `numar` în anul datei (fără deosebire de majuscule și spații): (numar, data, furnizor) sau None.
    Nu se numără NIR-ul refăcut acum (`refacut_din_id` — refacerea îi păstrează numărul) și nici NIR-urile deja înlocuite de refacerea lor
    (numărul lor trece la NIR-ul care le-a refăcut)."""
    n = " ".join(str(numar or "").split()).upper()
    an = str(data or "")[:4]
    if not n or not an.isdigit():
        return None
    try:
        rid = int(refacut_din_id) if str(refacut_din_id or "").strip() else None
    except (TypeError, ValueError):
        rid = None
    r = repo_stocuri.nir_cu_numarul(cur, schema, n, an, rid)
    return tuple(r.values()) if isinstance(r, dict) else r


def stocuri_nir_detaliu(tenant_id, nir_id, ctx):
    """[lotul 07.10 B, C11d] Un NIR salvat, deschis din „NIR-urile lunii”: antetul, articolele și notele lui, fiecare cu starea
    (ciornă / la validare / validată / respinsă, cu motivul)."""
    from core import stocuri_api as _s, coada_api as _coada
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _s.nir_detaliu(conn, schema, nir_id)
        if rez is None:
            raise _erori.Inexistent("NIR inexistent")
        stari = _coada.stari_note(conn, tenant_id, [n["id"] for n in rez["note"]])
        # [retest 07.10 R1] starea NIR-ului: din toate notele lui (și cele scoase la refacere — elementele din coadă rămân)
        _s.stare_validare_nir([rez["nir"]], {**_coada.stari_note(conn, tenant_id, _s.note_nir(rez["nir"])), **stari},
                              _s.refaceri_nir(conn, schema, [rez["nir"]["id"]]))
    for n in rez["note"]:
        n["validare"] = stari.get(n["id"])
    return rez


def stocuri_descarcare(tenant_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/descarcare`; docstringul ei a ramas in stratul HTTP.

    [lotul 12, C187, clasa 216] Descărcarea gestiunii global-valorice e nota care închide luna (K din rulajele cumulate „până la finele
    perioadei de referință”, OMFP 1802/2014 pct.286 alin.(4)): se scrie după ce luna s-a încheiat, ca salariile, amortizarea și reevaluarea
    în valută (`_uc_comun._cere_luna_incheiata`). Aceeași regulă pentru butonul din Stocuri și pentru cel de după raportul Z."""
    _uc_comun._cere_perioada(an, luna)   # luna 13 / anul greșit: refuz numit, nu `500` (ca la amortizare)
    _uc_comun._cere_luna_incheiata(an, luna, "Descărcarea gestiunii lunii")   # [lotul 12, C187, clasa 216]
    from core import stocuri_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        rez = _s.descarca_luna(conn, schema, an, luna)
    if rez.get("eroare"):
        if rez.get("ecran"):   # [lotul 07.10 pct.2] refuzul care trimite în alt ecran rămâne structurat (butonul spre el)
            raise _erori.CerereGresita(_uc_comun.refuz_spre_ecran(rez["eroare"], rez.get("cod"), rez["ecran"], rez.get("regula")))
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_articole(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [05.10.2026, comanda Costin pct.10] ecranul Stocuri arată Rețete numai la firma HoReCa (sau care are rețete)
        # [lotul 12, deficiența 473] `alimentatie_publica`: numai CAEN-ul HoReCa (`core/horeca.py`) — etichetele cotelor de pe Raport Z
        # („mâncare”, „alcool, sucuri”) descriu activitatea, nu existența unor rețete
        from core import horeca as _horeca
        with conn.cursor() as cur:
            _caen = repo_firma_profil.caen(cur, schema)
        return {"articole": _s.articole(conn, schema), "retete_vizibile": _s.retete_vizibile(conn, schema),
                "alimentatie_publica": _horeca.e_horeca(_caen)}


def cv_fisa(tenant_id, articol_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole/{articol_id}/fisa`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [lotul 11, deficiența 450, clasa „articol creat tacit lângă cel existent”] intrarea manuală cu „— articol nou —” și o denumire care
        # e deja a unui articol (`produse_api.cheie_denumire`: și fără diacritice) crea al doilea articol; acum refuz numit, ca NIR-ul (C11c)
        rez = None
        if not str((corp or {}).get("articol_id") or "").strip() and str((corp or {}).get("denumire") or "").strip():
            with conn.cursor() as _c:
                _ex = produse_api.articol_dupa_denumire(_c, schema, corp["denumire"])
            if _ex:
                _m = ("Articolul «%s» e deja în listă: alege-l de acolo — intrarea nu creează un al doilea articol cu același nume." % _ex[1])
                rez = {"eroare": {"mesaj": _m, "erori_campuri": [{"camp": "cv-den", "mesaj": _m}]}}
        try:
            _uc_comun._campuri_lipsa(corp, {"data": "cv-data", "cantitate": "cv-cant", "pret_unitar": "cv-pret"})   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            if not rez:
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            _uc_comun._campuri_lipsa(corp, {"articol_id": "cv-art", "data": "cv-data", "cantitate": "cv-cant"})   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            return _s.inventar(conn, schema, corp)
        except (ValueError, KeyError) as e:      # [lotul 6] refuzul ajunge ca mesaj, nu ca 500
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))


def cv_locatii(tenant_id, articol_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/locatii`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    with db.get_conn(schema) as conn:   # [C201] o singură conexiune ținută: verificarea articolului și locațiile, pe schema firmei
        # [lotul 7] Un articol care NU EXISTA intorcea `{"locatii": []}` — „articolul asta nu e
        # nicaieri" arata identic cu „articolul asta nu exista". Aceeasi clasa ca salariatul din
        # lotul 4 si contul din lotul 3.
        if articol_id is not None:
            with conn.cursor() as _cur:
                if not repo_stocuri.articolul_exista(_cur, articol_id):
                    raise _erori.Inexistent("articol inexistent")
        return {"locatii": _s.stoc_pe_locatii(conn, schema, articol_id)}


def cv_transfer(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/transfer`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            rez = _s.transfer(conn, schema, corp)   # [lotul 11, 440] `stocuri_cv_api.transfer` adună singur toate câmpurile (W3b)
        except (ValueError, KeyError) as e:   # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    if rez.get("erori_campuri"):   # [440] datele omului, toate deodată, fiecare lângă câmpul ei (ca înainte: 422 la corpul incomplet)
        raise _erori.DateInvalide({"mesaj": rez["eroare"], "erori_campuri": rez["erori_campuri"]})
    if rez.get("eroare"):
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def cv_reclasificare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/reclasificare`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            _uc_comun._campuri_lipsa(corp, {"articol_id": "rc-art", "cont_stoc_nou": "rc-cont", "data": "rc-data"})   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _s.analitica(conn, schema, zile_inert)


def cv_nivel_minim(tenant_id, articol_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/stocuri/articole/{articol_id}/nivel-minim`; docstringul ei a ramas in stratul HTTP."""
    from core import stocuri_cv_api as _s
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            rez = _s.set_barcode(conn, schema, articol_id, corp.get("barcode"))
        except _chei.CheieDublata as e:   # [lotul 10, C73 / U2] codul de bare al altui articol -> 422 pe câmpul `barcode`, cu articolul
            raise _erori.DateInvalide(e.detaliu())
    if rez is None:
        raise _erori.Inexistent("articol inexistent")
    return rez


def cabinet_categorie_marime(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/categorie-marime`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import categorie_marime as _cm
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    with db.get_conn(schema) as conn:
        return _cm.categorie(conn, schema, an)


def _tip_bilant(tip):
    if tip not in ("s1005", "s1003"):
        raise _erori.DateInvalide("Tipul bilanțului e S1005 sau S1003.")
    return tip


def bilant_an_precedent(tenant_id, an, tip, ctx):
    """[deficiența 221, decizia Costin 11.10.2026] De unde vine coloana „An precedent” a bilanțului `tip` pe `an` (bilanțul anului precedent
    din aplicație / evidența / completată manual / nicio sursă) și rândurile ei — ecranul Bilanț o spune și, unde lipsește, cere
    completarea manuală."""
    from psycopg2.extras import RealDictCursor
    from core import bilant as _b
    from core import bilant_api as _ba
    _uc_comun._cere_perioada(an=an)
    _tip_bilant(tip)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                # [deficiența 228] un an al cărui bilanț nu se poate întocmi deloc (31.12 dinaintea soldurilor de preluare) se spune ca
                # atare — ecranul îl pune lângă acțiunile inactive, nu „completează coloana”, care n-ar ajuta. [242] toate motivele deodată
                cp, _f10c = _ba.coloanele_verificate(cur, schema, tip, an)
            except _b.BilantOprit as e:
                # [varianta (a), 13.10.2026] refuzul spune și anii de închis — ecranul oferă propunerea notei de închidere pentru ei
                # afirmație TIPATĂ (DS cap.25): un fapt despre soldurile și rulajele firmei, cu temeiul completitudinii
                raise _erori.DateInvalide(_af.afirmatie(
                    "fapt", "bilant_oprit", str(e), an=e.an, luna=12, mesaj=str(e), cod="bilant_oprit", ani_inchidere=e.ani_inchidere, propuse=e.propuse,
                    temei_completitudine="soldurile la 31.12 și rulajele anului din notele validate ale firmei"))
            except ValueError as e:      # [deficiența 229] un an dinaintea înființării: bilanțul nu există
                raise _erori.DateInvalide(str(e))
    lipsa = [s for s in _ba.sectiuni(tip) if cp[s] is None]
    manual = [s for s in _ba.sectiuni(tip) if cp["sursa"][s] == "manual"]
    # afirmația despre coloană e TIPATĂ (DS cap.25): lipsa = absența observației, cu sursele în care s-a căutat; manualul = fapt, cu
    # temeiul completitudinii (cine a scris cifrele)
    if lipsa:
        afm = _af.afirmatie("absenta_observatie", "bilant_an_precedent", _ba.mesaj_coloana_goala(an, lipsa, cp.get("bilant_respins")), an=an - 1,
                            surse_consultate=["bilanțul %s pe %d validat în aplicație" % (tip.upper(), an - 1),
                                              "evidența pe %d din aplicație" % (an - 1)])
    elif manual:
        afm = _af.afirmatie("fapt", "bilant_an_precedent", _ba.avertisment_manual(an, manual, cp.get("manual"), cp.get("bilant_respins")), an=an - 1,
                            temei_completitudine="completată manual de contabil (exemplarul %d al coloanei)" % cp["manual"]["exemplar"])
    elif cp.get("infiintare"):
        # [deficiența 229] primul exercițiu: coloana e goală prin lege, nu prin lipsă — fapt, cu temeiul și data din Date firmă
        afm = _af.afirmatie("fapt", "bilant_an_precedent", _ba.nota_primul_exercitiu(an, cp["infiintare"]), an=an,
                            temei_completitudine="data înființării din Date firmă (%s); Legea 82/1991 art.27 alin.(8)"
                            % data_ro(cp["infiintare"]))
    else:
        afm = None
    return {"tip": tip, "an": an, "sursa": cp["sursa"], "lipsa": lipsa,
            "bilant": cp.get("bilant"), "manual": cp.get("manual"),
            "randuri": _ba.randuri_formular(tip),
            # [deficiența 227] denumirea fiecărui rând, de pe formular (structura ANAF), lângă numărul lui
            "denumiri": _ba.denumiri_formular(tip),
            # [deficiențele 233, 234] totalurile (fără câmp, calculate) și ordinea + codul rândurilor de pe formular
            "totaluri": _ba.totaluri_formular(tip),
            "ordine": _ba.ordine_formular(tip)[0], "coduri": _ba.ordine_formular(tip)[1],
            "valori": {s: cp[s] for s in _ba.sectiuni(tip)},
            "de_completat": [s for s in _ba.sectiuni(tip) if cp["sursa"][s] in (None, "manual")],
            "afirmatie": afm}


def bilant_inchidere_propunere(tenant_id, an, ctx):
    """[varianta (a), decizia Costin 13.10.2026, verbatim în DECIZII] „Aplicația propune, la cererea contabilului, nota de închidere la
    31.12: clasele 6/7 → 121 și regularizarea TVA 4426/4427 → 4423/4424. Nota apare ca propunere și intră în evidență numai după ce
    contabilul o validează (R36).” Notele se scriu CIORNĂ (`core/inchidere_an.py`); validarea e cea a oricărei note (Jurnal)."""
    from psycopg2.extras import RealDictCursor
    from core import inchidere_an as _ia
    from core.pdf_util import bani
    _uc_comun._cere_perioada(an=an)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                r = _ia.propune(cur, schema, an)
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
    if r["nimic"]:
        mesaj = ("La 31.12.%d nu e nimic de închis: clasele 6/7 și TVA (4426 / 4427) n-au sold în notele validate." % an)
    else:
        rez = r["rezultat"]
        ce = ("profit %s lei" % bani(rez)) if rez > 0 else (("pierdere %s lei" % bani(-rez)) if rez < 0 else "rezultat zero")
        # [deficiența 279, clasa] starea notelor (ciornă / trimise la validare) n-o știe ruta — o spune ecranul (`api.stareNota`)
        mesaj = ("Am propus la 31.12.%d: %s. Rezultatul închis în 121: %s. Notele intră în evidență numai după validare, "
                 "în Registrul jurnal, luna decembrie %d; apoi bilanțul se generează."
                 % (an, "; ".join("%s (%s, %s)" % (n["descriere"], n["document"] or "fără document",
                                                     _common.cate(len(n["linii"]), "linie", "linii")) for n in r["note"]), ce, an))
    return {"ok": True, "an": an, "mesaj": mesaj, "nimic": r["nimic"], "inlocuite": r["inlocuite"], "rezultat": str(r["rezultat"]),
            "note": [{"id": n["id"], "descriere": n["descriere"], "document": n["document"], "linii": n["linii"]} for n in r["note"]]}


def bilant_an_precedent_scrie(tenant_id, an, tip, corp, ctx):
    """[deficiența 221] Contabilul completează coloana „An precedent” pe secțiunile pe care aplicația nu le are (nici bilanțul anului
    precedent, nici evidența lui). Fiecare secțiune trimisă are TOATE rândurile-componente ale formularului, în lei întregi; totalurile le
    calculează serverul, ca formularul (deficiența 233 — unul trimis de ecran nu se citește); o secțiune pe care aplicația o are din bilanț
    sau din evidență nu se suprascrie manual. Se păstrează ca artefact (autor, moment, exemplar — cel vechi rămâne)."""
    import json
    from psycopg2.extras import RealDictCursor
    from core import artefacte as _art
    from core import bilant as _b
    from core import bilant_api as _ba
    _uc_comun._cere_perioada(an=an)
    _tip_bilant(tip)
    corp = corp or {}
    rand = _ba.componente_formular(tip)
    tot = _ba.totaluri_formular(tip)
    trimise = [s for s in _ba.sectiuni(tip) if s in corp]
    if not trimise or set(corp) - set(_ba.sectiuni(tip)):
        raise _erori.DateInvalide("Trimite coloana „An precedent” pe secțiunile %s." % " și / sau ".join(_ba.sectiuni(tip)))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cp = _ba.coloana_precedenta(cur, schema, tip, an)
            except ValueError as e:      # [deficiența 229] un an dinaintea înființării
                raise _erori.DateInvalide(str(e))
            m = _ba._ultimul(cur, schema, _ba.FEL_MANUAL, "%s:%d" % (tip, an))
        valori = json.loads(m["continut"]) if m else {}
        for s in trimise:   # starea coloanei (primul exercițiu, sursa din aplicație): refuz unic, înaintea valorilor
            if cp["sursa"][s] == _ba.PRIMUL_EXERCITIU:     # [deficiența 229] goală prin lege, nu se completează
                raise _erori.DateInvalide(_ba.nota_primul_exercitiu(an, cp["infiintare"]))
            if cp["sursa"][s] not in (None, "manual"):
                raise _erori.DateInvalide("Coloana „An precedent” %s vine din %s — nu se completează manual."
                                          % (s, "bilanțul pe %d din aplicație" % (an - 1) if cp["sursa"][s] == "bilant"
                                             else "evidența pe %d din aplicație" % (an - 1)))
        # [lotul 11, deficiența 440] rândurile lipsă și sumele care nu sunt lei întregi — pe TOATE secțiunile trimise, deodată
        er = _erori.ErorileFormularului("Coloana „An precedent” nu s-a salvat")
        for s in trimise:
            v = {k: x for k, x in (corp[s] if isinstance(corp[s], dict) else {}).items() if str(k).isdigit() and int(k) not in tot[s]}
            if sorted(int(k) for k in v) != rand[s]:
                er.camp(s, "Coloana „An precedent” %s se completează pe toate rândurile formularului (%d)." % (s, len(rand[s])))
                continue
            try:
                valori[s] = {str(k): int(x) for k, x in _b.cu_totaluri(tip, s, {int(k): int(str(x).strip() or 0) for k, x in v.items()}).items()}
            except (TypeError, ValueError):
                er.camp(s, "Coloana „An precedent” %s: fiecare rând e o sumă în lei întregi." % s)
        er.refuza()
        if "F20" in valori and "F30" in valori:
            # [C14] F20 și F30 cap.XIX se copiază amândouă din bilanțul depus; validatorul ANAF le compară — o neconcordanță se spune acum,
            # pe rânduri, nu la validare
            nec = _b.neconcordante_f20_f30({int(k): v for k, v in valori["F20"].items()}, {int(k): v for k, v in valori["F30"].items()})
            if nec:
                raise _erori.DateInvalide(_ba.mesaj_neconcordanta(an, nec))
        r = _art.pastreaza(conn, schema, _ba.FEL_MANUAL, "%s:%d" % (tip, an), json.dumps(valori, sort_keys=True),
                           produs_de_id=int(ctx["uid"]), produs_de=ctx.get("nume") or str(ctx["uid"]))
    return {"ok": True, "exemplar": r.get("exemplar"), "sectiuni": trimise}


def s1005_xml(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1005-xml`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            # [lotul 10, C69] refuzul cu trimitere (`RefuzGenerare`: Date firmă + câmpul lipsă) ajunge la ecran ca obiect
            raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    return {"xml": xml, "avertismente": av}


def s1005_valideaza(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1005-valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            xml, av = _ba.genereaza(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            # [lotul 10, C69] refuzul cu trimitere (`RefuzGenerare`: Date firmă + câmpul lipsă) ajunge la ecran ca obiect
            raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    # [deficiența 222, 11.10.2026] validatorul prin `duk.valideaza` — sursa unică (ca orice declarație): „ok” din fișierul DUK nu mai
    # ajunge pe ecran ca „erori” (caseta brută „ok” sub „Validare fără erori”), iar o rulare eșuată e gri cu motivul, nu „erori”.
    from core import duk as _duk_v
    _v = _duk_v.valideaza(xml, "s1005")
    ok = _v["stare"] == "valid"
    erori = _v["erori"] or ("" if ok else _v["temei"])
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
    from core import bilant as _bil   # [deficiența 188] rândurile care se depun, citite din XML-ul validat
    return {"ok": ok, "erori": erori, "avertismente": av, "randuri": _bil.randuri_din_xml(xml),
            "xml_b64": base64.b64encode(xml.encode()).decode()}


def s1003_xml(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1003-xml`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import bilant_api as _ba
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            # [lotul 10, C69] refuzul cu trimitere (`RefuzGenerare`: Date firmă + câmpul lipsă) ajunge la ecran ca obiect
            raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    return {"xml": xml, "avertismente": av}


def s1003_valideaza(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/s1003-valideaza`; docstringul ei a ramas in stratul HTTP."""
    import base64
    from core import bilant_api as _ba
    from core import artefacte as _art
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            xml, av = _ba.genereaza_s1003(conn, schema, an)
        except ValueError as e:
            # [bilant_422_v1] mesajul de refuz al lui bilant_api (ex. lipsa nr. reg. com.) e scris
            # pentru contabil; fara asta ajungea la el ca 500 gol (oprire generica, interzisa de DS).
            # [lotul 10, C69] refuzul cu trimitere (`RefuzGenerare`: Date firmă + câmpul lipsă) ajunge la ecran ca obiect
            raise _erori.DateInvalide(e.detaliu() if isinstance(e, _erori.RefuzGenerare) else str(e))
    # [deficiența 222, 11.10.2026] validatorul prin `duk.valideaza` — sursa unică (ca orice declarație): „ok” din fișierul DUK nu mai
    # ajunge pe ecran ca „erori” (caseta brută „ok” sub „Validare fără erori”), iar o rulare eșuată e gri cu motivul, nu „erori”.
    from core import duk as _duk_v
    _v = _duk_v.valideaza(xml, "s1003")
    ok = _v["stare"] == "valid"
    erori = _v["erori"] or ("" if ok else _v["temei"])
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
    from core import bilant as _bil   # [deficiența 188] rândurile care se depun, citite din XML-ul validat
    return {"ok": ok, "erori": erori, "avertismente": av, "randuri": _bil.randuri_din_xml(xml),
            "xml_b64": base64.b64encode(xml.encode()).decode()}


def retete_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _r.lista(conn, schema)


def retete_salveaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        return _r.sterge(conn, schema, reteta_id)


def retete_descarca(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/retete/descarca`; docstringul ei a ramas in stratul HTTP."""
    from core import retete_api as _r
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        try:
            rez = _r.descarca(conn, schema, corp)
        except (ValueError, KeyError) as e:      # [lotul 7] corp gol dadea `500`
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        from core import eticheta_nota as _et   # [258] nota de consum numită ca în Registrul jurnal (nu prin id)
        with conn.cursor() as _c:
            return _et.in_raspuns(_c, schema, rez)


def verificare_stocuri(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/verificare-stocuri`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import stocuri_cv as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                dif = (sold - vcv).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                rez.append({"cont": cont, "sold_contabil": str(sold.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                            "valoare_fise_cv": str(vcv.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                            "diferenta": str(dif), "ok": abs(dif) <= Decimal("0.01")})
    return {"conturi": rez, "ok": all(x["ok"] for x in rez),
            "nota": "Diferențele pot veni din note ciornă nevalidate sau din operațiuni în afara fișelor de magazie."}


def etransport_xml(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/etransport-xml`; docstringul ei a ramas in stratul HTTP."""
    import re
    from core import etransport as _e
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            r = repo_firma_profil.cui_firma(cur, schema) or {}
    cui = re.sub(r"\D", "", r.get("cui") or "")
    if not cui:
        raise _erori.DateInvalide(CUI_FIRMA_LIPSA)
    lipsa = _e.campuri_required_lipsa(corp)
    if lipsa:
        raise _erori.DateInvalide({"cod": "CAMPURI_LIPSA",
                "mesaj": "Câmpuri obligatorii lipsă (structura eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            r0 = repo_firma_profil.cui_firma_2(cur, schema)
    cui = _re2.sub(r"\D", "", (r0[0] if r0 else "") or "")
    if not cui:
        raise _erori.DateInvalide(CUI_FIRMA_LIPSA)
    lipsa = _egen.campuri_required_lipsa(corp)
    if lipsa:
        raise _erori.DateInvalide({"cod": "CAMPURI_LIPSA",
                "mesaj": "Câmpuri obligatorii lipsă (structura eTransport): " + "; ".join(x["eticheta"] for x in lipsa),
                "campuri": lipsa})
    try:
        xml = _egen.xml_notificare(cui, corp)
    except KeyError as e:
        raise _erori.DateInvalide("câmp lipsă: %s" % e)
    data_transport = (corp.get("transport") or {}).get("data")
    if not data_transport:
        raise _erori.DateInvalide("data transport lipsă")
    intracom = _es.uit_15_zile(str(corp.get("cod_tip_operatiune")))   # [3h · OUG 41/2022 art.11(2)] 15 zile: cod 10 (lit.a), 60 (lit.g), 80 (lit.j)
    mediu = os.environ.get("ETRANSPORT_MEDIU", os.environ.get("EFACTURA_MEDIU", "prod"))
    return _es.trimite(schema, principal, cui, xml, data_transport, intracom=intracom,
                       mediu=mediu, ref=corp.get("ref"))


def etransport_trimiteri_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/etransport/trimiteri`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            r = repo_banca.readuce_linia_de_extras(cur, schema, linie_id)
        conn.commit()
    if not r:
        raise _erori.DateInvalide("linia nu e ignorată")
    return {"ok": True}


def factura_recunoaste(tenant_id, factura_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/recunoaste`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.DateInvalide("factura nu e o ciornă de recunoaștere (starea ei: %s): actul e "
                                         "pentru facturile emise aduse prin import" % stare)
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


def factura_contabilizeaza(tenant_id, factura_id, ctx, confirma=False, nir_id=None, alta_livrare=False):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/contabilizeaza`; docstringul ei a ramas in stratul HTTP."""
    from core import contare_facturi as _cf
    from core import nir_legare as _nl
    # [lotul 11, C83] factura din XML în valută rămasă fără curs (BNR n-a răspuns la import): cursul BNR se aduce înaintea tranzacției,
    # iar contarea îl pune pe factură (`contare_facturi.curs_factura_importate`) — ieșirea reală a refuzului LIPSA_CURS_LEI
    with db.get_conn() as conn0:
        schema0 = auth_api.schema_tenant(conn0, ctx["uid"], tenant_id)
        with conn0.cursor() as cur0:
            _md = repo_efactura.moneda_si_data(cur0, schema0, factura_id) if schema0 else None
    if _md:
        _uc_comun._preincalzeste_cursul(*_md)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        from core import coada_api as _cq, note_derivate as _nd
        with conn.cursor() as _c0:   # [S3] notele respinse ale facturii (contarea + ieșirile), înainte de refacere
            _resp = [i for i in _cq.ciornele_documentului(_c0, schema, "factura-%d" % int(factura_id)) if _nd.respinsa(_c0, schema, i)]
            _vechi = _cq.amprente_note(_c0, _resp, schema)
            _motiv = _cq.motiv_respingere(_c0, schema, _resp[0]) if _resp else None
        try:
            with _cf.cursor_dict(conn) as cur:
                rez = _cf.contabilizeaza(cur, schema, factura_id, automat=False,
                                         nir_legat=_nl.alegerea(nir_id, alta_livrare))   # [decizia 08.10 pct.2]
            # [retest 07.10 R1] factura respinsă la validare, cu stocul stornat: refacerea ei reface și mișcarea de stoc
            from core import stocuri_anulare as _sa
            _stoc = _sa.reface_factura(conn, schema, factura_id)
            if _stoc is not None:
                rez = {**rez, "stoc": _stoc}
            if _resp:
                with conn.cursor() as _c1:
                    _noi = _cq.amprente_note(_c1, _cq.ciornele_documentului(_c1, schema, "factura-%d" % int(factura_id)), schema)
                _av = _cq.avertisment_neschimbata(_vechi, _noi, _motiv, confirma)
                if _av:
                    conn.rollback()
                    return _av
        except _cf.RefuzContare as e:
            conn.rollback()
            if e.cod == "INEXISTENTA":
                raise _erori.Inexistent(e.mesaj)
            # Codul de stare se pastreaza pe fiecare clasa de refuz: luna inchisa raspundea `423`
            # inainte de rescriere si raspunde `423` si acum. O rescriere care schimba tacit codul
            # de raspuns ar rupe apelanti fara sa spuna.
            if e.cod == "LUNA_INCHISA":
                raise _erori.Blocat(PERIOADA_INCHISA)
            if e.cod in _nl.CODURI:   # [decizia 08.10 pct.2] alegerea NIR-ului: candidații și propunerea, pentru ecran
                raise _erori.DateInvalide(_nl.detaliu_refuz(e))
            raise _erori.DateInvalide(e.mesaj)
        from core import eticheta_nota as _et   # [258] nota contării numită ca în Registrul jurnal (nu prin id)
        with conn.cursor() as _c:
            _et.in_raspuns(_c, schema, rez)
        conn.commit()
    return rez


def _vanzare_din_stoc(cur, schema, iid, fel, ies, articol, cantitate, pret_vanzare, pret_cumparare, tva, client, document):
    """[lotul 13, 548] Vânzarea și ieșirea ei din stoc, legate (`vanzari_din_stoc`, `core/migrare_vanzari_stoc.py`): jurnalul marjei citește
    de aici; nota vânzării nu se șterge cât ieșirea e vie (triggerul bazei)."""
    repo_operatiuni.vanzare_din_stoc_scrie(cur, schema, iid, fel, ies["id"], ies.get("inregistrare_id"), articol[0], cantitate, pret_vanzare,
                               pret_cumparare, tva, client[0], client[1], document)


def vanzare_marja(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-marja`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 548, comanda Costin 13.1] „Vânzarea nu descarcă bunul din gestiune (607 = 371) și nu cere clientul; profitul iese
    mai mare cu tot costul bunului, stocul rămâne umflat. Prețul de cumpărare se scrie de mână în loc să vină din bunul aflat în stoc.”
    Acum: bunul se alege din stoc (marfă, 371) și iese din gestiune la CMP (`stocuri_cv_api.iesire`: 607 = 371, cu documentul vânzării);
    prețul de cumpărare al marjei = valoarea ieșirii; clientul e partenerul rândurilor 4111. Rămân corecte (Costin): TVA pe marjă prin sută
    mărită, marja negativă -> TVA 0 fără report (norme pct.86). CF art.312 alin.(1) lit.g): „marja profitului este diferența dintre prețul
    de vânzare aplicat de persoana impozabilă revânzătoare și prețul de cumpărare”."""
    from core import tva_marja as _m, compensari_api as _cz
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("articol", "cantitate", "pret_vanzare", "cota", "client_nume", "document"))   # [lotul 11, 440 / A4]
            pv = Decimal(str(corp["pret_vanzare"]))
            cota = _common.cota_ceruta(corp)
        except (ValueError, KeyError, ArithmeticError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        cant = _cantitate_pozitiva(corp["cantitate"], "op-cantitate")
        client = (_cz.cui_partener(corp.get("client_cui")) or None, str(corp["client_nume"]).strip())
        document = str(corp["document"]).strip()
        with conn.cursor() as cur:
            _cere_stoc_pe_articol(cur, schema, "Vânzarea în regim de marjă din stoc")
            art = _articol_stoc(cur, schema, corp["articol"], "371", "op-articol")
        ies = _iesire_din_stoc(conn, schema, art, cant, corp["data"], document)
        cost = Decimal(str(ies["valoare"]))
        try:
            r = _m.vanzare_marja(pv, cost, cota)
        except ValueError as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], (corp.get("descriere") or "Vânzare în regim de marjă (art. 312) %s"
                                                                                       % art[1])[:200], document_ref=document)[0]
            # [1a · CF art.312, norme pct.86] Nota se face la PRETUL DE VANZARE (ce datoreaza clientul): 707 = pret_vanzare - TVA pe marja;
            # 4427 = TVA (0 la marja negativa, FARA report - metoda pe fiecare livrare, pct.86).
            for d, c, s in (("4111", "707", pv - r["tva"]), ("4111", "4427", r["tva"])):
                if s > 0:
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, d, c, s, client[0], client[1])
            _vanzare_din_stoc(cur, schema, iid, "marja", ies, art, cant, pv, cost, r["tva"], client, document)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, dict(_af.afirmatie(
        "fapt", "vânzare în regim de marjă", r["nota"] or "marjă calculată conform art. 312",
        unde=_Unde("inregistrare", iid),
        temei_completitudine="prețul de vânzare și prețul de cumpărare = valoarea ieșirii din stoc "
                             "(Cod fiscal art. 312, regimul marjei)"),
        inregistrare_id=iid, nota_iesire_id=ies.get("inregistrare_id"), pret_cumparare=str(cost), marja_bruta=str(r["marja_bruta"]),
        tva=str(r["tva"]), marja_neta=str(r["marja_neta"]), avertisment=r["nota"]))


def vanzare_marja_turism(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-marja-turism`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import tva_marja_turism as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("calitate_client",))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            regim = _m.determina_regim(corp["calitate_client"], corp.get("locuri", ["RO"]),
                                       _uc_comun.bifa(corp, "optiune_normal", False),
                                       _uc_comun.bifa(corp, "intermediar", False))
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
                r = _m.comision_intermediar(corp["comision"], _common.cota_ceruta(corp), _uc_comun.bifa(corp, "tva_inclus", False))
                linii = [("4111", "704", r["baza"])]
                if r["tva"] > 0:
                    linii.append(("4111", "4427", r["tva"]))
                rasp = {"regim": regim, "baza": str(r["baza"]), "tva": str(r["tva"]),
                        "total": str(r["total"])}
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], (corp.get("descriere") or f"Vanzare marja turism ({regim}, art. 311)")[:200])[0]
            for d, c, s in linii:
                if s > 0:
                    repo_contabilitate.adauga_linie_2(cur, schema, iid, d, c, s)
        conn.commit()
    rasp["inregistrare_id"] = iid
    return _uc_comun.cu_eticheta(schema, rasp)


def vanzare_aur_investitii(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-aur-investitii`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 548, comanda Costin 13.1] „Vânzarea nu descarcă bunul din gestiune (costul aurului) și nu cere clientul”. Acum: aurul
    se alege din stoc (marfă, 371) și iese din gestiune la CMP (`stocuri_cv_api.iesire`: 607 = 371, cu documentul livrării); clientul
    (numele și identificarea, CF art.313 alin.(10)) e partenerul rândului 4111. Rămân corecte (Costin): refuzul sub 995‰ (art.313 alin.(1)
    lit.a)), livrarea scutită 4111 = 707 fără TVA; opțiunea de taxare către o persoană impozabilă -> taxare inversă (art.331 alin.(2) lit.h))."""
    from core import tva_aur as _m, compensari_api as _cz
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("articol", "cantitate", "tip", "puritate", "calitate_client", "client_identificare", "client_nume",
                                            "suma", "document"))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            ok, motiv = _m.este_aur_investitii(corp["tip"], corp["puritate"],
                                               corp.get("an_emisie"), corp.get("pret_unitar"),
                                               corp.get("valoare_aur"))
            if not ok:
                raise ValueError("nu este aur de investiții: " + motiv)
            regim = _m.livrare_aur(_uc_comun.bifa(corp, "optiune_taxare", False),
                                   corp["calitate_client"], corp["client_identificare"])
            suma = Decimal(str(corp["suma"]))
            if suma <= 0:
                # [G5 · P7] Constrangerea in mesaj, nu doar verdictul: cod de dinainte de val, intrat
                # in domeniul lui G5 odata cu mutarea corpului rutei din `main.py` in use-case.
                raise ValueError("Suma livrării trebuie să fie mai mare decât 0; "
                                 "primit: %s." % suma)
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        cant = _cantitate_pozitiva(corp["cantitate"], "op-cantitate")
        ident = str(corp["client_identificare"]).strip()
        client = ((_cz.cui_partener(ident) or None) if corp["calitate_client"] == "PJ" else None, str(corp["client_nume"]).strip())
        document = str(corp["document"]).strip()
        with conn.cursor() as cur:
            _cere_stoc_pe_articol(cur, schema, "Livrarea aurului de investiții din stoc")
            art = _articol_stoc(cur, schema, corp["articol"], "371", "op-articol")
        ies = _iesire_din_stoc(conn, schema, art, cant, corp["data"], document)
        mentiune = "taxare inversă (art. 331 alin. (2) lit. h)" if regim == "taxare_inversa" \
                   else "scutit (art. 313 alin. (3))"
        descr = (corp.get("descriere") or "Livrare aur de investiții %s" % art[1]) + " - " + mentiune + " - client: " + ident
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], document_ref=document)[0]
            repo_contabilitate.adauga_linie_partener(cur, schema, iid, "4111", "707", suma, client[0], client[1])
            _vanzare_din_stoc(cur, schema, iid, "aur", ies, art, cant, suma, Decimal(str(ies["valoare"])), Decimal("0"), client, document)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "regim": regim, "suma": str(suma), "nota_iesire_id": ies.get("inregistrare_id"),
                                          "cost": str(ies["valoare"])})


def achizitie_agricultor(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-agricultor`; docstringul ei a ramas in stratul HTTP."""
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("data", "valoare", "agricultor_in_registru", "cont_cheltuiala"))   # [lotul 11, 440 / A4]
            agr = _partener_din_corp(corp.get("agricultor_cui"), corp.get("agricultor_nume"), "agricultor", "agricultorul (CNP sau CUI)")   # [lotul 13, 549 / 506] partenerul achiziției
            r = _m.achizitie_de_la_agricultor(corp["valoare"], _uc_comun.bifa(corp, "agricultor_in_registru"))
            # [R54] confruntarea cu planul firmei inlocuieste verificarea de PREZENTA:
            # `cere_cont` refuza si absenta, si contul care nu exista in plan, si spune CE
            # cont si UNDE se creeaza. Doua verificari suprapuse ar fi doua locuri.
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achiziție de la agricultor, regim special (art. 315^1)") + " - " + agr[1] + \
            ((" - " + r["mentiune"]) if r.get("mentiune") else "")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], "borderou_achizitie")[0]
            for d, c, s in [(cont, "401", r["pret"]), ("4426", "401", r["compensatie"])]:
                if s > 0:   # [549] fără compensație, fără rândul 4426
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, d, c, s, agr[0], agr[1])
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"]), "avertisment": r.get("mentiune")})


def vanzare_agricultor(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-agricultor`; docstringul ei a ramas in stratul HTTP."""
    from core import tva_agricultori as _m
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            r = _m.compensatie(corp["pret"])
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Livrare produse agricole") \
                + " - regim special agricultori (art. 315^1), compensație 8%"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for s in (r["pret"], r["compensatie"]):
                repo_contabilitate.adauga_linie_venit_servicii(cur, schema, iid, s)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "pret": str(r["pret"]),
            "compensatie": str(r["compensatie"]), "total": str(r["total"])})


def cabinet_fisa_cont(tenant_id, an, cont, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/fisa-cont`; docstringul ei a ramas in stratul HTTP."""
    from core import fisa_cont as _fc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                # [lotul 10, deficiența 425] Cartea mare pornește din soldul preluat + notele dinainte, iar în anul preluării cu rulaje,
                # din soldul de la 1 ianuarie + rulajul preluat — aceeași regulă ca balanța (`fisa_cont.sold_initial_preluat`)
                _si, _rul = _fc.sold_initial_preluat(conn, schema, cont, an, luna)
                fisa = _fc.pentru_json(_fc.fisa_cont(conn, schema, cont, an, luna, sold_initial=_si, rulaj_preluat=_rul))
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
    return {"an": an, "luna": luna, "formular": _fc.COD_FORMULAR,
            "conturi": conturi, "fisa": fisa}


def jurnal_marja(tenant_id, tip, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal-marja`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 548] Jurnalul vânzărilor în regim de marjă (second-hand, CF art.312): pe fiecare vânzare prețul de vânzare, prețul
    de cumpărare (valoarea ieșirii din stoc), marja și TVA-ul pe marjă — din `vanzari_din_stoc`, nu din textul notei. Înainte: „cost” era
    primul rând al notei (707, adică prețul fără TVA), iar o vânzare cu altă explicație decât „(art. 312)” lipsea. Vânzările dinainte de
    lotul 13 (fără ieșire din stoc) apar din notă, cu prețul de cumpărare necunoscut („—”: nu era în evidență). Turismul (art.311) rămâne
    citit din note, ca înainte."""
    marker = {"secondhand": "art. 312", "turism": "art. 311"}.get(tip)
    if not marker:
        raise _erori.DateInvalide("tip invalid (secondhand|turism)")
    if len(luna) != 7 or luna[4] != "-":
        raise _erori.DateInvalide("luna format YYYY-MM")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        from core import eticheta_nota as _et   # [258] nota numită ca în Registrul jurnal (nu prin id)
        note = {}
        with conn.cursor() as cur:
            if tip == "secondhand":
                for iid, data, descr, status, pv, pc, tva, client, doc in repo_operatiuni.vanzari_marja_luna(cur, schema, luna):
                    note[iid] = {"id": iid, "data": str(data), "descriere": descr, "status": status, "client": client, "document": doc,
                                 "pret_vanzare": Decimal(str(pv)), "cost": Decimal(str(pc)), "marja_neta": Decimal(str(pv)) - Decimal(str(pc)) - Decimal(str(tva)),
                                 "tva": Decimal(str(tva))}
            rows = repo_contabilitate.linii_pentru_jurnal_marja(cur, schema, "%" + marker + "%", luna)
            vechi = {}
            for iid, data, descr, status, cont, suma, _lid in rows:
                if iid in note:
                    continue
                n = vechi.setdefault(iid, {"id": iid, "data": str(data), "descriere": descr, "status": status, "client": None, "document": None,
                                           "pret_vanzare": Decimal("0"), "cost": None, "marja_neta": Decimal("0"), "tva": Decimal("0")})
                n["pret_vanzare"] += suma
                if cont == "4427":
                    n["tva"] += suma
                elif tip == "turism" and n["cost"] is None:
                    n["cost"] = suma
                else:
                    n["marja_neta"] += suma
            if tip == "secondhand":   # nota veche: 707 = prețul fără TVA, nu marja; marja nu se poate socoti fără prețul de cumpărare
                for n in vechi.values():
                    n["marja_neta"] = None
            note.update(vechi)
            _etj = dict(_et.note(cur, schema, set(note)))
    lista = sorted(note.values(), key=lambda n: (n["data"], n["id"]))
    tot = lambda k: sum((n[k] for n in lista if n[k] is not None), Decimal("0"))   # noqa: E731
    s = lambda v: None if v is None else str(v)   # noqa: E731
    return {"tip": tip, "luna": luna, "numar_note": len(lista),
            "note": [{**n, "eticheta": _etj.get(n["id"]), "pret_vanzare": s(n["pret_vanzare"]), "cost": s(n["cost"]),
                      "marja_neta": s(n["marja_neta"]), "tva": s(n["tva"])} for n in lista],
            "total_vanzari": str(tot("pret_vanzare")), "total_cost": str(tot("cost")), "total_baza_marja_neta": str(tot("marja_neta")),
            "total_tva_colectata": str(tot("tva"))}


def calcul_cm_endpoint(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/calcul-cm`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import salarizare as _s
    from core import scadente as _scad
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    # [lotul 4, 04.09.2026] Trei defecte, toate aici. `{}` cadea cu `KeyError` NEPRINS (`500`);
    # `luna=13` mergea pana la capat si intorcea o indemnizatie calculata — cu alta baza, fiindca
    # fereastra de 6 luni se muta —, iar `zile_lucratoare_cm=-5` trecea tacut, cu `brut 0`. *O
    # indemnizatie de concediu medical calculata pe o luna care nu exista e o cifra care intra in
    # stat, in D112 si in decontul cu CNAS.*
    try:
        _uc_comun._campuri_lipsa(corp, ("an", "luna", "salariat_id", "zile_lucratoare_cm"), prefix="")   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
        an, luna = int(corp["an"]), int(corp["luna"])
        sal_id = int(corp["salariat_id"])
        zile_cm = int(corp["zile_lucratoare_cm"])
    except (KeyError, TypeError, ValueError) as e:
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e) if isinstance(e, KeyError) else
                                "Anul, luna, salariatul și zilele de concediu medical se așteaptă ca "
                                "numere întregi: %s" % e)
    _uc_comun._cere_perioada(an, luna)
    if zile_cm < 0:
        raise _erori.DateInvalide("Zilele de concediu medical nu pot fi negative (s-a primit %d). "
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
        raise _erori.DateInvalide("Nu se poate calcula media: salariatul nu are nicio lună lucrată în cele "
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
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        # [lotul 11, C86] factura emisă venită din e-Factura (importată) e deja transmisă: refuzul numit, înaintea conexiunii SPV (nu „conectează
        # SPV” pentru o factură care nu trebuie trimisă); `trimite` îl are și el, ca poarta 0, pentru orice alt apelant
        din_ef = _eft.refuz_din_efactura(conn, schema, factura_id) if schema else None
    if not schema:
        raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    if din_ef:   # [lotul 11, AT] afirmația tipată, întreagă (`fapt` despre factură, cu `cod` și `mesaj`), nu reîmpachetată ca proză
        raise _erori.Conflict(dict(din_ef))
    principal = _spv_rute.spv_principal(ctx)   # token owner (cabinet XOR gratuit); 403 daca niciunul
    mediu = os.environ.get("EFACTURA_MEDIU", "prod")
    try:
        r = _eft.trimite(schema, factura_id, principal, mediu=mediu)
    except _efs.EDateIncomplete as e:
        # [lotul 10, C69] datele firmei lipsă trimit la Date firmă (butonul + câmpul), ca refuzul generatoarelor
        raise _erori.DateInvalide(e.detaliu() if getattr(e, "ecran", None) else str(e))
    except NotImplementedError as e:
        raise _erori.DateInvalide("Tip de factură netratat încă în e-Factura: %s" % e)
    st = r.get("stare")
    if st == "din_efactura":   # [lotul 11, C86] poarta 0 a lui `trimite` (factura importată între verificarea de mai sus și trimitere)
        raise _erori.Conflict(dict(r))
    if st == "fara_token":
        # [deficiența 289b] refuzul are buton spre Setări cont → Conectare SPV (`ecran_destinatie.ECRANE.conectare_spv`)
        raise _erori.Conflict(_uc_comun.refuz_spre_ecran(r.get("mesaj"), COD_SPV_NECONECTAT, "conectare_spv"))
    if st == "fara_drept" or r.get("fara_drept"):
        # [17.10.2026, decizia Costin pct.2] certificatul conectat n-are drept SPV pe CUI-ul firmei: spus exact, cu ce are de făcut
        raise _erori.Conflict(_uc_comun.refuz_spre_ecran(r.get("mesaj"), COD_SPV_FARA_DREPT, "conectare_spv"))
    if st == "deja_trimisa":
        raise _erori.Conflict("Factura are deja o trimitere activă în SPV (%s)." % r.get("stare_existenta"))
    if st == "in_curs":   # [lotul 10, C73 / U2] a doua trimitere simultană a aceleiași facturi -> 409 numit, înainte de încărcare
        raise _erori.Conflict(r["mesaj"])
    if st == "nevalidat":
        return {"stare": "nevalidat", "erori": r.get("validare_mesaje", [])}
    return {"stare": st, "index_incarcare": r.get("index_incarcare"),
            "execution_status": r.get("execution_status"),
            "erori": r.get("errors") or ([r.get("raspuns", "")] if st in ("nok", "eroare_upload") else []),
            # [lotul 10, C73 / U2] «investigatie»: încărcată peste o trimitere vie — mesajul numește dublura
            "mesaj": r.get("mesaj") if st == "investigatie" else r.get("raspuns")}


#: [lotul 6 pct.7c, 273] ce nu vine din XML-ul facturii primite și se cere la validare (refuzuri structurate: `camp` = câmpul din ecran)
REFUZ_TERT_PLATITOR = {"cod": "TERT_PLATITOR_DE_COMPLETAT", "camp": "pr-platitor", "mesaj":
                       "Spune dacă furnizorul e înregistrat în scopuri de TVA: din XML nu se poate afla, iar D394 îl declară după tipul lui."}
REFUZ_CATEGORIE_331 = {"cod": "CATEGORIE_331_DE_COMPLETAT", "camp": "pr-c331", "mesaj":
                       "Factura e cu taxare inversă (linii „AE”): alege categoria produsului (art.331), pe care D394 o declară cu codul ei."}
COD_SPV_NECONECTAT = "SPV_NECONECTAT"   # [289b] textul: `efactura_trimitere.MESAJ_FARA_TOKEN`
COD_SPV_FARA_DREPT = "SPV_FARA_DREPT"   # [17.10.2026] textul: `spv_conector.MESAJ_FARA_DREPT`


def facturi_trimiteri_spv(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/trimiteri-spv`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            rows = repo_efactura.ultima_trimitere_per_factura(cur, schema)
    return {str(r[0]): {"stare": r[1], "index_incarcare": r[2], "error_message": r[3]} for r in rows}


def facturi_primite_lista(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        out = []
        with conn.cursor() as cur:
            rows = repo_efactura.primite_in_asteptare(cur, schema)
            for (pid, cife, cifb, status, xmlb, fid) in rows:
                pr = repo_efactura.contul_invatat_al_emitentului(cur, schema, cife)
                info = {"id": pid, "cif_emitent": cife, "status": status, "factura_id": fid,
                        "cont_sugerat": pr[0] if pr else ""}
                try:
                    f = _ef.parseaza_xml((xmlb or "").encode("utf-8"), cifb)
                    # [lotul 6 pct.7c, 273] ce nu vine din XML și trebuie completat de contabil înainte de validare: tipul
                    # furnizorului pentru D394 (înregistrat în scopuri de TVA sau nu) și, la taxarea inversă, categoria produsului (codul
                    # D394). [16.10.2026, 273 pct.4] Plătitorul facturii (un terț) nu e element UBL / RO_CIUS și nu se declară în D394.
                    de_completat = ["dacă furnizorul e înregistrat în scopuri de TVA (D394)"] + (
                        ["categoria produsului cu taxare inversă (D394)"] if f.get("taxare_inversa") else [])
                    info.update({"parsabila": True, "furnizor": f.get("tert_nume"), "furnizor_cod_tva": f.get("furnizor_cod_tva"),
                                 "numar": f.get("numar"), "data": str(f.get("data_emitere") or ""),
                                 "total": str(f.get("total") or ""), "tva": str(f.get("tva") or ""),
                                 "moneda": f.get("moneda"), "taxare_inversa": bool(f.get("taxare_inversa")),
                                 "de_completat": de_completat,
                                 "linii": [{"descriere": l["descriere"], "cantitate": str(l["cantitate"]),
                                            "pret": str(l["pret_unitar"]), "cota": str(l["cota_tva"])}
                                           for l in (f.get("linii") or [])]})
                except Exception as e:
                    info.update({"parsabila": False, "eroare_parse": str(e)[:200]})
                out.append(info)
    # [deficiența 418a] statutul de TVA al furnizorului (și TVA la încasare) din XML și ANAF, la data facturii — cu conexiunea închisă (un
    # apel ANAF nu ține o conexiune din pool); ce rămâne neaflat se cere contabilului
    from core import anaf_api as _anaf
    _st = _anaf.statut_furnizori([(i["cif_emitent"], i["data"], i.get("furnizor_cod_tva")) for i in out if i.get("parsabila") and i.get("data")])
    for i in out:
        if i.get("parsabila") and i.get("data"):
            i["statut_furnizor"] = _st[(i["cif_emitent"], i["data"])]
            if i["statut_furnizor"]["platitor_tva"] is not None:
                i["de_completat"] = [x for x in i["de_completat"] if not x.startswith("dacă furnizorul e înregistrat")]
    # [lotul 11, deficiența 444, comanda Costin 11.1 pct.20] „când numele de la ANAF diferă de fișa partenerului, se spune și se propune
    # actualizarea”: fișa furnizorului cu CIF-ul emitentului, față de numele ANAF (`clienti_api.compara_cu_anaf`, sursa unică a comparației)
    cu_nume = [i for i in out if (i.get("statut_furnizor") or {}).get("denumire_anaf")]
    if cu_nume:
        with db.get_conn(schema) as conn, conn.cursor() as cur:
            for i in cu_nume:
                # aceeași formă ca răspunsul `verifica-cui` (`denumire` + `fise` cu `diferit`), deci ecranul o arată cu același ajutor
                # (`static/js/ecrane/nume_anaf.js` propuneNumeAnaf) ca NIR-ul și casa
                i["fisa_vs_anaf"] = dict(clienti_api.compara_cu_anaf(cur, i["cif_emitent"], i["statut_furnizor"]["denumire_anaf"]),
                                         denumire=i["statut_furnizor"]["denumire_anaf"])
    from core import d394 as _d394
    # categoriile art.331 (codul produsului în D394), pentru alegerea din validare — din `d394.CODPR`, sursa unică
    return {"primite": out, "categorii_331": sorted(_d394.CODPR)}


def factura_primita_xml(tenant_id, primita_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite/{primita_id}/xml`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant_citire(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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


def _platitor_tva_strict(cui):
    """[lotul 13, 544] Plătitor de TVA (art.316) după ANAF, pentru CUI-ul dat: True / False; CUI negăsit -> refuz lângă câmp; ANAF care nu
    răspunde -> refuz „reîncearcă” (nu se presupune nimic)."""
    from core import anaf_api as _anaf
    try:
        r = _anaf.valideaza_cui([cui])
    except Exception as e:  # noqa: BLE001 — orice cădere a serviciului ANAF e „nu se poate verifica acum”, spusă contabilului
        _obs.esec_secundar("anaf_platitor_ti", e)
        raise _erori.ServiciuStrainCazut("ANAF nu răspunde acum, deci nu se poate verifica dacă furnizorul %s e înregistrat în scopuri de "
                                         "TVA — taxarea inversă se aplică numai între plătitori (CF art.331 alin.(1)). Încearcă din nou peste "
                                         "câteva minute." % cui)
    if not r or not r[0].get("gasit"):
        m = ("CUI-ul %s nu e găsit la ANAF: taxarea inversă cere un furnizor înregistrat în scopuri de TVA (CF art.331 alin.(1)). Verifică "
             "CUI-ul de pe factură." % cui)
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-furnizor_cui", "mesaj": m}]})
    return bool(r[0].get("platitor_tva"))


def achizitie_taxare_inversa(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-taxare-inversa`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from datetime import date as _date
    from core import taxare_inversa as _ti
    # ── [P5 val 3, 11.09.2026] ANAF ÎNAINTE de conexiune ────────────────────────────────
    # Statutul TVA al furnizorului se îngheață pe factură și depinde doar de payload. Forma
    # dinainte îl cerea din interiorul tranzacției, deci ținea o conexiune din pool peste un apel
    # cu termen de 20 s. `platitor_tva_freeze` e best-effort: ANAF jos → fallback, nu excepție.
    furnizor_cui = str(corp.get("furnizor_cui") or "").strip().upper().replace(" ", "")
    # [lotul 13, deficiența 544, comanda Costin 13.1] „cu «Furnizor plătitor TVA: Nu» s-a aplicat taxarea inversă (4426 = 4427 6.300); art. 331
    # o permite doar când ambii parteneri sunt plătitori. Refuză; calitatea de plătitor se verifică la ANAF din CUI, nu se întreabă de mână.”
    # CF art.331 alin.(1): taxarea inversă se aplică „pentru livrările de bunuri și prestările de servicii […] efectuate de persoane
    # impozabile înregistrate în scopuri de TVA conform art. 316” către beneficiari înregistrați la fel. Verdictul ANAF e cerut STRICT: fără
    # el (CUI negăsit, ANAF căzut) nu se aplică taxarea inversă din presupunere — înainte, „Nu” scris de om era înlocuit tăcut de ANAF, iar
    # ANAF căzut lăsa „Da” implicit.
    _tert_pl = _platitor_tva_strict(furnizor_cui) if furnizor_cui else None
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            rand = repo_firma_profil.platitor_tva(cur, schema)
            beneficiar_tva = bool(rand[0]) if rand else True
        from core import facturi_api as _fa
        try:
            # [lotul 11, deficiența 440] câmpurile lipsă, CUI-ul și numărul facturii — toate deodată, fiecare lângă câmpul ei
            _er = _erori.ErorileFormularului("Achiziția nu s-a înregistrat")
            _uc_comun._campuri_lipsa(corp, ("categorie", "valoare", "data", "cota"), er=_er)
            if not furnizor_cui:      # calculat înaintea blocului; validarea rămâne aici (422)
                _er.camp("op-furnizor_cui", "CUI furnizor obligatoriu (taxare inversă e intre plătitori RO - furnizor cu CUI)")
            if not str(corp.get("numar") or "").strip():
                _er.camp("op-numar", "număr factura furnizor obligatoriu")
            _er.refuza()
            categorie = str(corp["categorie"])
            ok, mentiune = _ti.se_aplica(categorie, corp["valoare"],
                                         _tert_pl,   # verdictul ANAF / bifa citita corect — nu sirul „false” (adevarat)
                                         beneficiar_tva,
                                         _date.fromisoformat(corp["data"]))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            val = Decimal(str(corp["valoare"]))
            cota = _common.cota_ceruta(corp)
            tva = _ti.tva_beneficiar(val, cota)
            numar = str(corp.get("numar") or "").strip()
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achiziție") + " - " + mentiune
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor RO cu CUI, categorie_331 -> codPR, taxare_inversa=True)
            #    = sursa citita de D394 (op1 tip C + op11 codPR). Linie cota reala -> baza/tva reverse-charge.
            # `_tert_pl` s-a înghețat înaintea blocului — v. nota de la începutul rutei
            try:   # [10.10.2026] refuzul motivat al emiterii ajunge la contabil (422), nu ca 500 (deficiența C7, generalizată)
                fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                           linii=[{"descriere": descr[:200], "cantitate": 1,
                                                   "pret_unitar": str(val), "cota_tva": cota}],
                                           tert_nume=furnizor_nume or None, tert_cui=furnizor_cui,
                                           categorie_331=categorie, taxare_inversa=True, status="importata",
                                           tert_platitor_tva=_tert_pl)
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge 4426=4427, NU cea standard
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            for d, c, s in [(cont, "401", val), ("4426", "4427", tva)]:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva),
            "mentiune": mentiune})


def achizitie_ic(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-ic`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    from core import repo_d301_operatiuni_api as _repo_d301
    from core import curs_bnr as _cb
    # [lotul 13, deficiența 537] suma în valuta facturii + cursul BNR al zilei EXIGIBILITĂȚII (CF art.290 alin.(2): „ultimul curs de schimb
    # comunicat de Banca Națională a României […] valabil la data la care intervine exigibilitatea taxei”; exigibilitatea AIC: CF art.284
    # alin.(2)); datoria către furnizor se ține în valută (factura în moneda ei), ca reevaluarea lunară și diferența de curs la plată să
    # se poată calcula. RON rămâne pentru factura în lei.
    # `valoare` e suma din factura furnizorului, în moneda ei; o cerere fără monedă (API-ul de dinainte) e în lei
    _moneda = str(corp.get("moneda") or "RON").strip().upper()
    if _moneda and _moneda != "RON" and corp.get("data"):
        _uc_comun._preincalzeste_cursul(_moneda, str(_common.exigibilitate_aic(corp["data"], corp.get("data_faptului_generator"))))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        from core import facturi_api as _fa
        try:
            # [lotul 11, deficiența 440] câmpurile lipsă, codul de TVA UE, numărul facturii și tipul — toate deodată, fiecare lângă câmp
            _er = _erori.ErorileFormularului("Achiziția intracomunitară nu s-a înregistrat")
            _uc_comun._campuri_lipsa(corp, ("valoare", "data", "cota"), er=_er)
            if not str(corp.get("cod_tva_furnizor") or "").strip():
                _er.camp("op-cod_tva_furnizor", "codul de TVA al furnizorului din UE e obligatoriu (fără el achiziția nu ajunge în D390)")
            else:
                # [C128, lotul 12] furnizorul dintr-un ALT stat membru (CF art.273 alin.(1), art.307 alin.(2)): „RO…” e o achiziție internă
                try:
                    _ic.valideaza_aic(str(corp.get("cod_tva_furnizor")).strip().upper().replace(" ", ""))
                except ValueError as _e_aic:
                    _er.camp("op-cod_tva_furnizor", str(_e_aic))
            if not str(corp.get("numar") or "").strip():
                _er.camp("op-numar", "număr factura furnizor obligatoriu")
            # [lotul 5, 04.09.2026] `tip` se citea cu un `if ... == "servicii" else bunuri`: orice
            # altceva — inclusiv o valoare gresita — devenea BUNURI, tacut. Probat cu
            # `tip="altceva"`: `200`, si achizitia a intrat in evidenta ca bunuri. Nu e o nuanta:
            # tipul decide incadrarea in D390 (bunuri vs servicii) si temeiul citat pe nota.
            if corp.get("tip") not in ("bunuri", "servicii"):
                _er.camp("op-tip", nomenclator_cerut("tip", "bunuri|servicii"))
            _er.refuza()
            val_valuta = Decimal(str(corp["valoare"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # [R148] Art. 291 alin. (8): pentru AIC cota e cea in vigoare la data EXIGIBILITATII,
            # nu la data facturii. Cele doua difera cand factura furnizorului vine tarziu — atunci
            # exigibilitatea a intervenit deja, in ziua 15 a lunii urmatoare faptului generator
            # (art. 284 alin. 2). Aplicatia calcula deja exact asta pentru D390 (`d390.py:491`) si
            # valida cota pe alta data: doua date pentru acelasi fapt.
            _data_exig = _common.exigibilitate_aic(corp["data"], corp.get("data_faptului_generator"))
            if _moneda == "RON":
                curs, data_curs = Decimal("1"), _data_exig
            else:
                try:
                    curs, data_curs, _src = _cb.curs_pentru(conn, _moneda, _data_exig)
                except _cb.MonedaNecotata as _mn:
                    raise _erori.DateInvalide({"mesaj": str(_mn), "erori_campuri": [{"camp": "op-moneda", "mesaj": str(_mn)}]})
                except _cb.CursIndisponibil as _ci:
                    raise _erori.Conflict(str(_ci))
            val = (val_valuta * Decimal(str(curs))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            tva = _ic.tva_taxare_inversa(
                val, _common.cota_ceruta({**corp, "data": _data_exig.isoformat()}))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            cod_tva_furnizor = str(corp.get("cod_tva_furnizor") or "").strip().upper().replace(" ", "")
            # [etapa 2, lotul F, 15.09.2026] TARA furnizorului, derivata din chiar codul lui de TVA.
            # Fara ea factura se scria cu implicitul `tert_tara="RO"`, iar D300 ruteaza pe TARA
            # (`d300.py:247-249`), nu pe codul partenerului: achizitia intracomunitara nu ajungea
            # nici la rd.5/rd.18 (bunuri), nici la rd.7/rd.20 (servicii). Nota contabila purta
            # taxarea inversa, decontul nu declara nimic — doua evidente care spun lucruri diferite
            # despre acelasi fapt. Prefixul se desparte cu helperul care stie si lista UE si cazul
            # Greciei (`intracomunitar.desparte_cod_tva`), nu cu `cod[:2]` scris aici: un `RO` scris
            # de doua ori e inceputul unei divergente.
            tara_furnizor, _nr_tva = _ic.valideaza_aic(cod_tva_furnizor)
            numar = str(corp.get("numar") or "").strip()
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
            data_fg = corp.get("data_faptului_generator") or None
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        tip = "servicii intracomunitare primite (art. 278 alin. (2))" if corp.get("tip") == "servicii"               else "achiziție intracomunitară de bunuri (art. 268)"
        with conn.cursor() as _curp:
            _benef_platitor = bool((repo_firma_profil.platitor_tva(_curp, schema) or [True])[0])
        _linii_ti, _ment_ti = _ic.note_taxare_inversa(cont, val, tva, _benef_platitor)
        descr = (corp.get("descriere") or "AIC") + f" - {tip}, {_ment_ti}"
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # 1) rand FACTURA (directie=primita, furnizor UE) = sursa citita de D390. Factura UE fara TVA RON
            #    (taxare inversa la beneficiar) -> linie cota 0 -> total=val, tva=0 -> baza D390 = val.
            try:   # [10.10.2026] refuzul motivat al emiterii ajunge la contabil (422), nu ca 500 (deficiența C7, generalizată)
                fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                           linii=[{"descriere": descr[:200], "cantitate": 1,
                                                   "pret_unitar": str(val_valuta), "cota_tva": 0}],
                                           moneda=_moneda, curs=None if _moneda == "RON" else curs,
                                           data_curs=None if _moneda == "RON" else data_curs, curs_sursa=None if _moneda == "RON" else "bnr",
                                           tert_nume=furnizor_nume or None, tert_cui=cod_tva_furnizor,
                                           tert_tara=tara_furnizor,
                                           # [R186, 16.09.2026] AXA, INGHETATA pe document. `corp["tip"]`
                                           # e deja validat contra nomenclatorului mai sus (bunuri|servicii,
                                           # orice altceva = refuz), deci ce se scrie e ce a declarat omul.
                                           # Pana azi valoarea intra doar in textul descrierii, iar D300
                                           # rutata pe implicit: serviciile IC ajungeau la rd.5, nu la rd.7.
                                           axa_ic=corp.get("tip"),
                                           data_faptului_generator=data_fg, status="importata")
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
            fid = fres["factura_id"]
            # 2) contabilizare LEGATA (factura_id) - nota specializata reverse-charge, NU cea standard
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            for d, c, s in _linii_ti:
                repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
            # [DECIZII 66] intrare UNICA: aceeasi achizitie scrie SI operatiunea D301 (pentru D301),
            # legata de factura -> D390 o ia din factura (op-ul legat e sarit), fara dubla numarare.
            _a, _l, _z = corp["data"].split("-")
            _repo_d301.insert_d301_operatiuni(
                cur, schema, int(_a), int(_l), 1 if corp.get("tip") == "bunuri" else 5,
                numar, "%s.%s.%s" % (_z, _l, _a), val_valuta, _moneda, curs, tva,
                # [lotul 13, 539 / 537] codul fără prefixul țării (țara stă în coloana ei): D301 afișa „IEIE6388047V”
                tara_furnizor, _nr_tva, furnizor_nume or "", None, factura_id=fid)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "tva": str(tva),
                                          "moneda": _moneda, "valoare_valuta": str(val_valuta), "curs": str(curs),
                                          "data_curs": str(data_curs), "exigibilitate": str(_data_exig)})


def achizitie_neinregistrat(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/achizitie-neinregistrat`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import facturi_api as _fa
    from core import d394 as _d394
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
            # [deficiența 402] borderoul de achiziție identifică vânzătorul persoană fizică: domiciliul și actul de identitate (OMFP
            # 2634/2015 anexa 1 pct.2: „menționarea părților care participă la efectuarea operațiunii”). *INTERPRETARE CU TEMEI:* datele de
            # identificare ale unei persoane fizice = domiciliul și actul de identitate (ca la borderoul 14-4-13); CNP-ul nu se cere (nu
            # îl cere nicio normă citată aici). De reconfirmat dacă apare o normă care transează.
            adresa_pf = str(corp.get("furnizor_adresa") or "").strip()
            act_pf = str(corp.get("furnizor_act") or "").strip()
            # [lotul 10, deficiența 402, comanda Costin 10.2 pct.7b, verbatim] „refuzurile la contul de stoc fără articol spun doar «articolul» /
            # «cantitatea».” Fiecare câmp lipsă primește fraza întreagă (ce lipsește și de ce), iar refuzul le numește pe TOATE deodată
            # (clasa 410): (câmpul, mesajul de lângă el, numele lui în fraza refuzului)
            # [lotul 11, deficiența 440] și numele vânzătorului, valoarea și categoria intră în ACEEAȘI listă (înainte, numele și valoarea
            # refuzau singure, înaintea celorlalte)
            lipsa_pf = [x for x in (("op-furnizor_nume", "Scrie numele vânzătorului (persoana fizică): apare în D394 (denP) și pe "
                                     "borderou.", "numele vânzătorului") if not furnizor_nume else None,
                                    ("op-furnizor_adresa", "Scrie domiciliul vânzătorului (localitatea, strada, numărul): borderoul îl "
                                     "identifică.", "domiciliul vânzătorului") if not adresa_pf else None,
                                    ("op-furnizor_act", "Scrie actul de identitate al vânzătorului (seria și numărul): borderoul îl "
                                     "identifică.", "actul lui de identitate (seria și numărul)") if not act_pf else None) if x]
            lipsa_stoc = []
            try:
                val = Decimal(str(corp.get("valoare")))
            except ArithmeticError:
                val = None
            # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
            lipsa_val = [] if (val is not None and val.is_finite() and val > 0) else [
                ("op-valoare", "Valoarea operațiunii trebuie să fie un număr mai mare decât zero.", "valoarea")]
            if not str(corp.get("data") or "").strip():
                lipsa_val.append(("op-data", "Scrie data borderoului de achiziție.", "data"))
            categorie = str(corp.get("categorie") or "").strip() or None
            lipsa_cat = []
            if categorie == "cereale":
                # [lotul 11, 449/450] D394 declară cerealele achiziționate (op. N) cu SUBCODUL NC, nu cu centralizatorul 21 („la op11 codul 21
                # NU e valid”, `d394._op11_cod`): „Cereale” trecea la scriere și cădea abia la declarație („cereale fără subcodul NC”)
                lipsa_cat.append(("op-categorie", "La cereale și plante tehnice D394 cere codul NC al bunului (HG 1/2016 pct.109 alin.(7)): "
                                                  "alege-l din listă (ex. 1001 Grâu și meslin, 1005 Porumb).", "codul NC al cerealelor"))
            elif categorie and not _d394.codpr_N_din_categorie(categorie):
                lipsa_cat.append(("op-categorie", "categoria N invalidă (nomenclatorul de la lit.D, codurile de produs N): %s" % categorie,
                                  "categoria"))
            cont = _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala")  # [R54]
            # [deficiența 402] OMFP 2634/2015 anexa 1 pct.6: „Documentele justificative provenite din [...] cumpărare a unor bunuri de la
            # persoane fizice, pe bază de borderou de achiziție [...] pot fi înregistrate în contabilitate numai în cazul în care se face
            # dovada intrării în gestiune a bunurilor respective.” Pe un cont de stoc: articolul și cantitatea, iar intrarea în fișă
            import psycopg2.extras as _E
            from core import documente_interne as _documente_interne, metoda_stoc as _ms
            la_stoc = any(cont.startswith(p) for p in ("371", "301", "302", "303"))
            articol = " ".join(str(corp.get("articol") or "").split())
            cant = Decimal(str(corp.get("cantitate") or 0)) if str(corp.get("cantitate") or "").strip() else Decimal(0)
            # [lotul 11, deficiența 450 — comanda Costin 11.1 pct.9, verbatim] „borderoul de achiziție a creat tacit un articol nou «grau»
            # lângă cel existent. Articolul se alege din nomenclator; unul nou se creează doar la cerere explicită.” Cauza: intrarea în stoc
            # primea numai denumirea, iar `stocuri_cv_api.intrare` fără `articol_id` creează MEREU un articol (F1: articolele 5 și 6, „grau”).
            # Acum: `articol_id` = articolul ales din listă; `articol_nou` = cererea explicită (refuzată dacă denumirea e deja a unui articol,
            # după `produse_api.cheie_denumire` — fără deosebire de majuscule, spații și diacritice, ca NIR-ul, C11c); o denumire fără cerere
            # explicită se ia numai dacă e deja în nomenclator (nu se creează nimic). Articolul nu se mai creează niciodată tacit.
            articol_ales = None   # (id, denumire, um) al articolului existent
            articol_nou = _uc_comun.bifa(corp, "articol_nou", False)
            um_stoc = "buc"   # borderoul pe cheltuială: o linie, un serviciu / o achiziție
            if la_stoc:
                with conn.cursor(cursor_factory=_E.RealDictCursor) as _c:
                    metoda = _ms.citeste(_c, schema)
                    if str(corp.get("articol_id") or "").strip():
                        _r = repo_stocuri.articolul_ales(_c, schema, corp["articol_id"])
                        articol_ales = (_r["id"], _r["denumire"], _r["um"]) if _r else None
                        if not _r:
                            lipsa_stoc.append(("op-articol", "Articolul ales nu mai e în nomenclator: alege-l din nou din listă.",
                                               "articolul (din listă)"))
                    elif articol:
                        articol_ales = produse_api.articol_dupa_denumire(_c, schema, articol)
                        if articol_ales and articol_nou:
                            lipsa_stoc.append(("op-articol_den", "Articolul «%s» e deja în nomenclator: alege-l din listă — borderoul nu "
                                               "creează un al doilea articol cu același nume." % articol_ales[1], "articolul (din listă)"))
                        elif not articol_ales and not articol_nou:
                            lipsa_stoc.append(("op-articol", "Articolul «%s» nu e în nomenclator: alege-l din listă sau cere explicit un "
                                               "articol nou." % articol, "articolul (din listă sau unul nou, cerut explicit)"))
                if metoda == _ms.GV:
                    raise ValueError("La stocul global-valoric, marfa cumpărată intră în gestiune prin NIR, la prețul de vânzare: "
                                     "înregistrează achiziția cu un NIR, pe care treci borderoul ca document.")
                if articol_ales and not lipsa_stoc:
                    articol = articol_ales[1]
                # [lotul 12, C115] UM-ul liniei borderoului și al intrării în stoc: al articolului ales din nomenclator (stocul lui se ține în
                # unitatea lui), al celui nou cerut explicit — cel ales pe ecran; „buc” numai când nici unul nu are
                # [lotul 13, regula UM — `facturi.MESAJ_UM_LIPSA`] fără UM nici la articol, nici pe ecran: nu „buc”, ci cerut lângă câmp
                um_stoc = (articol_ales[2] if articol_ales else None) or str(corp.get("um") or "").strip() or None
                if articol and not um_stoc:
                    from core import facturi as _fc_um
                    lipsa_stoc.append(("op-um", _fc_um.MESAJ_UM_LIPSA, "unitatea de măsură"))
                if not articol and not lipsa_stoc:
                    lipsa_stoc.append(("op-articol", "Alege articolul care intră în stoc pe contul %s (din nomenclator, sau unul nou, cerut "
                                                     "explicit): marfa intră în gestiune odată cu borderoul." % cont, "articolul"))
                if cant <= 0:
                    lipsa_stoc.append(("op-cantitate", "Scrie cantitatea care intră în stoc pe contul %s, mai mare decât zero, în "
                                                       "unitatea de măsură a articolului." % cont, "cantitatea"))
            if lipsa_pf or lipsa_val or lipsa_stoc or lipsa_cat:   # [402] refuzul numit, cu TOATE câmpurile lui ([440]: și valoarea, categoria)
                refuz = {"mesaj": " ".join(x for x in (
                    ("Borderoul de achiziție identifică vânzătorul: completează %s." % " și ".join(t for _c, _m, t in lipsa_pf))
                    if lipsa_pf else None,
                    " ".join(m for _c, m, _t in lipsa_val) or None,
                    ("Pe contul de stoc %s, borderoul aduce marfa în gestiune odată cu el (OMFP 2634/2015 anexa 1 pct.6): completează %s."
                     % (cont, " și ".join(t for _c, _m, t in lipsa_stoc))) if lipsa_stoc else None,
                    " ".join(m for _c, m, _t in lipsa_cat) or None) if x),
                    "erori_campuri": [{"camp": c, "mesaj": m} for c, m, _t in lipsa_pf + lipsa_val + lipsa_stoc + lipsa_cat]}
                raise _erori.DateInvalide(refuz)
            # [lotul 11, deficiența 450] „După generare, formularul nu trebuie să permită dublarea notei.” Serverul, nu numai ecranul: borderourile
            # firmei se scriu unul după altul (lacăt pe tranzacție), iar un borderou FĂRĂ număr scris, identic cu unul viu (nestornat) — aceeași
            # dată, același vânzător, aceeași valoare, același articol și aceeași cantitate — e a doua trimitere a aceluiași formular: refuz
            # numit, nimic scris. O a doua cumpărare, de același fel, își scrie numărul (alt document), iar numărul scris trece prin 434.
            from core import repo_borderou
            with conn.cursor() as _c:
                repo_borderou.blocheaza_borderourile(_c, schema)
                if not " ".join(str(corp.get("numar") or "").split()):
                    _dublu = _borderou_identic(_c, schema, corp["data"], furnizor_nume, val, (articol if la_stoc else None),
                                               (cant if la_stoc else Decimal(1)))
                    if _dublu:
                        _msg = ("Borderoul acesta e deja înregistrat: %s din %s (%s, %s lei), cu nota lui. Nimic nu s-a scris a doua oară. "
                                "Dacă e o a doua cumpărare, de același fel, scrie-i numărul în «Nr. borderou»."
                                % (_dublu[0], data_ro(_dublu[1]), furnizor_nume, bani(val)))
                        refuz = {"mesaj": _msg, "cod": COD_BORDEROU_DUBLAT, "erori_campuri": [{"camp": "op-numar", "mesaj": _msg}]}
                        raise _erori.DateInvalide(refuz)
            # [lotul 10, deficiența 434] „Numerotarea borderourilor e unică și continuă”: numărul aplicației continuă după cel mai mare
            # borderou al anului (`documente_interne.cel_mai_mare`), iar un număr scris de mână care e deja al altui borderou se refuză
            # lângă câmp (indexul unic din bază, `migrare_borderou_numar_unic`, îl oprește și pe orice alt drum)
            numar = " ".join(str(corp.get("numar") or "").split())
            if numar:
                with conn.cursor() as _c:
                    _dubla = _documente_interne.borderou_cu_numarul(_c, schema, numar, corp["data"])
                    _urm = _documente_interne.cel_mai_mare(_c, schema, "borderou_achizitie", str(corp["data"])[:4]) + 1
                if _dubla:
                    # DS cap.6 v2.89 „un mesaj, o singură dată”: lângă câmp — al cui e numărul și ce se poate face; jos — regula
                    _msg = ("Numărul %s e deja al borderoului din %s (%s). Lasă câmpul gol, iar aplicația dă numărul următor (%s%d), "
                            "sau scrie alt număr." % (_dubla[0], data_ro(_dubla[1]), _dubla[2] or "vânzător fără nume",
                                                      _documente_interne.PREFIX_BORDEROU, _urm))
                    refuz = {"mesaj": "Numerotarea borderourilor e unică: un număr nu se dă de două ori în același an.",
                             "erori_campuri": [{"camp": "op-numar", "mesaj": _msg}]}
                    raise _erori.DateInvalide(refuz)
            else:
                numar = _documente_interne.PREFIX_BORDEROU + str(_documente_interne.urmatorul(conn, schema, "borderou_achizitie",
                                                                                              corp["data"]))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Achiziție de la neînregistrat") + " - " + furnizor_nume
        with conn.cursor() as cur:
            tranzactie.fixeaza_schema(cur, schema)
            # tert_cui GOL -> clasifica_partener -> tip_partener 2 (N); PF nu factureaza TVA -> linie cota 0.
            # `tert_pf=True` (23.08.2026): pana azi lipsa codului era declarata DOAR in comentariul de
            # deasupra, iar garda noua de la `cere_cod_partener` n-avea cum s-o citeasca. Achizitia de la
            # o persoana neinregistrata E cazul legitim fara cod - acum o spune CODUL, nu proza.
            try:   # [10.10.2026] refuzul motivat al emiterii ajunge la contabil (422), nu ca 500 (deficiența C7, generalizată)
                # [401] documentul e BORDEROUL de achiziție (OMFP 2634/2015, cod 14-4-13), nu o factură: `tip = 'borderou'`
                fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                           linii=[{"descriere": (articol if la_stoc else descr)[:200], "cantitate": str(cant) if la_stoc else 1,
                                                   "pret_unitar": str((val / cant).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) if la_stoc else str(val),
                                                   "cota_tva": 0, "um": um_stoc}],
                                           tert_nume=furnizor_nume, tert_cui="", tert_adresa=adresa_pf, categorie_331=categorie,
                                           status="importata", tert_platitor_tva=False, tert_pf=True, tip="borderou")
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
            fid = fres["factura_id"]
            repo_facturi.seteaza_act_identitate(cur, schema, fid, act_pf)
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, descr[:200])[0]
            repo_contabilitate.adauga_linie_furnizor(cur, schema, iid, cont, val)
            intrare = None
            if la_stoc:   # [402] intrarea în gestiune, odată cu borderoul (la cost: valoarea borderoului / cantitate)
                from core import eticheta_nota as _et, stocuri_cv_api as _scv
                # [450] articolul ales (sau găsit în nomenclator) intră cu id-ul lui; numai cererea explicită creează unul nou
                intrare = _scv.intrare(conn, schema, {"articol_id": articol_ales[0] if articol_ales else None,
                                                     "denumire": articol, "um": um_stoc, "cantitate": str(cant),
                                                     "pret_unitar": str((val / cant).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)), "cont_stoc": cont,
                                                     "data": corp["data"], "document": _et.factura(cur, schema, fid)}, factura_id=fid)
                if intrare.get("eroare"):
                    refuz = intrare["eroare"]
                    raise _erori.DateInvalide(refuz)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "factura_id": fid, "valoare": str(val), "numar": numar,
            "nota_linii": [{"debit": cont, "credit": "401", "suma": str(val)}],   # [lotul 11, 8c] conturile notei, pe ecran după generare
            "intrare_stoc": ({"articol": articol, "articol_id": intrare.get("articol_id"), "cantitate": str(cant),
                              "articol_nou": not articol_ales} if intrare else None),
            "categorie": categorie, "in_d394": bool(categorie)})


#: [lotul 11, 450] a doua trimitere a aceluiași borderou (formularul retrimis după generare)
COD_BORDEROU_DUBLAT = "BORDEROU_DUBLAT"


def _borderou_identic(cur, schema, data, vanzator, valoare, articol, cantitate):
    """[450] Borderoul VIU (nici stornare, nici stornat) identic cu cel trimis: aceeași dată, același vânzător (fără deosebire de majuscule și
    spații), aceeași valoare și o linie cu același articol (`produse_api.cheie_denumire`; None = borderoul pe cheltuială, fără articol) și
    aceeași cantitate. (numar, data) sau None."""
    from decimal import Decimal
    from core import repo_borderou
    # valoarea = suma notei pe 401 (valoarea scrisă de om), nu totalul liniei, rotunjit la preț unitar cu 2 zecimale
    for fid, numar, d, tert in repo_borderou.vii_cu_data_si_valoarea(cur, schema, data, valoare):
        if " ".join(str(tert or "").split()).casefold() != " ".join(str(vanzator or "").split()).casefold():
            continue
        for desc, c in repo_borderou.descriere_si_cantitate(cur, schema, fid):
            if (articol is None or produse_api.cheie_denumire(desc) == produse_api.cheie_denumire(articol)) and \
                    Decimal(str(c)) == Decimal(str(cantitate)):
                return (numar, d)
    return None


def borderouri_lista(tenant_id, an, luna, ctx):
    """[lotul 11, 450 / decizia 10.3] Borderourile de achiziție ale lunii (ecranul „Borderou de achiziție”): numărul, data, vânzătorul,
    valoarea (suma notei pe 401), articolul și cantitatea, nota și legătura de stornare (stornat de / stornarea lui)."""
    _uc_comun._cere_perioada(an, luna)
    from core import eticheta_nota as _et
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        from core import repo_borderou
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            out = []
            for f in [dict(x) for x in repo_borderou.ale_lunii(cur, schema, an, luna)]:
                l = repo_borderou.prima_linie(cur, schema, f["id"]) or {}
                n = repo_borderou.nota_si_valoarea(cur, schema, f["id"])
                out.append({"id": f["id"], "numar": f["numar"], "data": str(f["data_emitere"]), "vanzator": f["tert_nume"],
                            "eticheta": _et.factura(cur, schema, f["id"]), "articol": l.get("descriere"),
                            "cantitate": str(l["cantitate"]) if l.get("cantitate") is not None else None, "um": l.get("um"),
                            "valoare": str(n["valoare"]) if n else None, "inregistrare_id": n["id"] if n else None,
                            "nota_eticheta": _et.nota(cur, schema, n["id"]) if n else None, "nota_status": n["status"] if n else None,
                            "storno_din": _et.factura(cur, schema, f["storno_din_id"]) if f["storno_din_id"] else None,
                            "stornat_de": _et.factura(cur, schema, f["stornat_de_id"]) if f["stornat_de_id"] else None})
    # categoria bunului pentru D394 op. N (lit.D, `d394.CODPR_N`), cu cerealele pe subcodul NC (`produse_api.NC_CEREALE`, HG 1/2016 pct.109
    # alin.(7)) în locul centralizatorului, nevalid la op11: lista formularului vine de aici, nu se scrie a doua oară în ecran
    from core import d394 as _d394
    categorii = [{"cod": nc, "eticheta": "Cereale: %s (NC %s)" % (den, nc)} for nc, den in produse_api.NC_CEREALE.items()] + [
        {"cod": k, "eticheta": ETICHETE_N[k]} for k in _d394.CODPR_N if k != "cereale"]
    return {"borderouri": out, "categorii_n": categorii}


#: [lotul 11] denumirile categoriilor D394 op. N de pe formularul borderoului (aceleași ca înainte, în Operațiuni); cheile = `d394.CODPR_N`
#: fără „cereale” (gard: core/test_lot11_b_450_borderou.py)
ETICHETE_N = {"deseuri": "Deșeuri", "masa_lemnoasa": "Masă lemnoasă", "terenuri": "Terenuri", "constructii": "Construcții",
              "alte_bunuri": "Alte bunuri", "alte_servicii": "Alte servicii"}


def borderou_storneaza(tenant_id, factura_id, corp, ctx):
    """[lotul 11, decizia Costin 10.3 pct.4, verbatim] „Borderoul se corectează prin stornare, ca factura.”

    Până azi borderoul nu se putea corecta deloc: ștergerea îl refuza (are notă — `facturi_api.sterge_factura`, „corectezi prin storno”),
    iar stornarea îl refuza și ea („se storneaza doar facturi emise”) — un drum închis la ambele capete.

    Stornarea = AL DOILEA document, legat de primul, nu o corectare a lui (ca `facturi_api.storneaza`): un borderou nou, cu numărul următor
    (BA-n), `storno_din_id` = borderoul stornat, aceeași linie cu cantitatea cu minus; nota inversă (aceleași conturi, sumele cu minus —
    stornarea în roșu, OMFP 1802/2014 pct.69: „corectarea cu semnul minus a operațiunii inițiale”); intrarea lui în stoc, stornată în roșu
    (`anuleaza_id`, valoarea exact a intrării), legată de borderoul de stornare. Refuzuri numite, nimic scris: borderoul e deja stornat,
    e el însuși o stornare (CF art.330 alin.(1) lit.b), ca la factură — C74), marfa lui a ieșit deja din stoc, stornarea e datată înaintea
    lui sau într-o lună închisă. Indexul unic `facturi_borderou_storno_uniq` oprește și a doua stornare simultană."""
    import datetime as _dt
    from decimal import Decimal
    import psycopg2 as _pg
    from core import facturi_api as _fa, documente_interne as _di, eticheta_nota as _et, stocuri_anulare as _sa
    from core import repo_stocuri as _rs, stocuri_cv as _scvm
    corp = corp or {}
    data = str(corp.get("data") or _dt.date.today().isoformat())[:10]
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, data)
        from core import repo_borderou
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            repo_borderou.blocheaza_borderourile(cur, schema)
            f = repo_borderou.de_stornat(cur, schema, factura_id)
            if not f:
                raise _erori.Inexistent("Borderoul de achiziție nu există.")
            et = _et.factura(cur, schema, f["id"])
            if f["storno_din_id"]:
                # [lotul 10, C74 — aceeași regulă ca la factură] stornarea anulează valorile documentului corectat
                raise _erori.DateInvalide("%s e el însuși o stornare (a documentului %s): o stornare nu se stornează la rândul ei "
                                          "(CF art.330 alin.(1) lit.b))." % (et, _et.factura(cur, schema, f["storno_din_id"])))
            deja = repo_borderou.stornarea_lui(cur, schema, f["id"])
            if deja:
                raise _erori.DateInvalide("%s e deja stornat prin %s: nu mai rămâne nimic de stornat (CF art.330 alin.(1) lit.b))."
                                          % (et, _et.factura(cur, schema, deja["id"])))
            if _dt.date.fromisoformat(data) < f["data_emitere"]:
                raise _erori.DateInvalide({"mesaj": "Stornarea nu se datează înaintea borderoului (%s): alege data de azi sau una după el."
                                                    % data_ro(f["data_emitere"]),
                                           "erori_campuri": [{"camp": "ba-storno-data", "mesaj": "Data stornării e înaintea borderoului."}]})
            linii = [dict(x) for x in repo_borderou.linii_de_stornat(cur, schema, f["id"])]
            linii_nota = [dict(x) for x in repo_borderou.liniile_notei(cur, schema, f["id"])]
            intrari = [dict(x) for x in repo_borderou.intrari_vii(cur, schema, f["id"])]
            repo_borderou.savepoint_stornare(cur)   # un refuz de mai jos nu lasă nimic scris (nici numărul), oricine ar fi apelantul

        def _renunta(mesaj):
            with conn.cursor() as _c:
                repo_borderou.inapoi_la_stornare(_c)
            return _erori.DateInvalide(mesaj)
        numar = _di.PREFIX_BORDEROU + str(_di.urmatorul(conn, schema, "borderou_achizitie", data))
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            tranzactie.fixeaza_schema(cur, schema)
            try:
                fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=data, directie="primita",
                                           linii=[{"descriere": ("STORNO: " + (l["descriere"] or ""))[:200], "um": l["um"] or "buc",
                                                   "cantitate": str(-abs(Decimal(str(l["cantitate"])))), "pret_unitar": str(l["pret_unitar"]),
                                                   "cota_tva": 0} for l in linii],
                                           tert_nume=f["tert_nume"], tert_cui="", tert_adresa=f.get("tert_adresa"),
                                           categorie_331=f.get("categorie_331"), status="importata", tert_platitor_tva=False, tert_pf=True,
                                           tip="borderou")
            except ValueError as e:
                raise _renunta(str(e))
            sid = fres["factura_id"]
            try:
                repo_borderou.leaga_stornarea(cur, schema, f["id"], sid, lambda cur, e: _chei.CheieDublata(
                    "%s a fost stornat între timp de altă cerere. Stornarea ta nu s-a scris; reîncarcă lista ca s-o vezi pe cea făcută." % et))
            except _chei.CheieDublata as e:
                raise _renunta(str(e))
            repo_facturi.seteaza_act_identitate(cur, schema, sid, f.get("tert_act_identitate"))
            et_s = _et.factura(cur, schema, sid)
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, data, sid, ("Stornare %s - %s" % (et, f["tert_nume"] or ""))[:200])
            iid = iid["id"] if isinstance(iid, dict) else iid[0]
            for l in linii_nota:   # nota inversă: aceleași conturi, sumele cu minus (stornare în roșu)
                repo_contabilitate.adauga_linie(cur, schema, iid, l["cont_debit"], l["cont_credit"], -Decimal(str(l["suma"])))
            stornate = []
            for m in intrari:   # intrarea în stoc a borderoului, stornată în roșu, legată de borderoul de stornare
                try:
                    stornate.append(repo_borderou.storneaza_intrarea(
                        cur, schema, m, max(_dt.date.fromisoformat(data), m["data"]), ("Stornare: " + et)[:100], sid,
                        lambda cur, e: _chei.CheieDublata("%s a fost stornat între timp de altă cerere: intrarea lui în stoc e deja stornată."
                                                          % et)))
                    _scvm.fisa_magazie(_rs.miscari_ale_articolului(cur, schema, m["articol_id"]))
                except (ValueError, _pg.errors.RaiseException) as e:
                    if isinstance(e, _chei.CheieDublata):
                        raise _renunta(str(e))
                    if isinstance(e, _pg.errors.RaiseException) and _sa.MARCAJ_STOC_NEGATIV not in str(e):
                        raise
                    _ex = _renunta("")   # refuzul de stoc (regula din bază) nu lasă tranzacția abandonată și nimic scris
                    den = (repo_stocuri.denumirea_articolului(cur, schema, m["articol_id"]) or {}).get("denumire") or "articolul"
                    raise _erori.DateInvalide("Stornarea nu s-a făcut: %s a adus în stoc %s, iar marfa a ieșit deja. Stornarea intrării ar lăsa "
                                              "stocul negativ. Anulează întâi ieșirile care au folosit-o, apoi stornează borderoul." % (et, den)) from _ex
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"factura_id": sid, "numar": numar, "storno_din_id": f["id"], "eticheta": et_s,
                                          "inregistrare_id": iid, "miscari_stornate": stornate,
                                          "nota_linii": [{"debit": l["cont_debit"], "credit": l["cont_credit"], "suma": str(-Decimal(str(l["suma"])))}
                                                         for l in linii_nota],
                                          "mesaj": "%s stornează %s: nota inversă e ciornă, de validat în Registrul jurnal." % (et_s, et)})


def import_extracomunitar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/import-extracomunitar`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        with conn.cursor() as cur:
            rand = repo_firma_profil.platitor_tva_2(cur, schema)
            platitor = bool(rand[0]) if rand else True
        try:
            # [lotul 5] `procent_taxa_vamala=500` trecea: taxa vamala 5.000 la o valoare
            # vamala de 1.000, baza TVA 6.000. Un procent e o parte dintr-un intreg.
            _uc_comun._campuri_lipsa(corp, ("data", "valoare_vamala", "cota", "numar_dvi", "furnizor_nume", "cont_destinatie"))
            _ptv = corp.get("procent_taxa_vamala", 0) or 0
            if not (0 <= float(_ptv) <= 100):
                raise ValueError("Procentul taxei vamale e între 0 și 100 — s-a primit %s. Taxa "
                                 "vamală e o parte din valoarea în vamă, nu un multiplu al ei."
                                 % (_ptv,))
            r = _ie.calcul_import(corp["valoare_vamala"],
                                  corp.get("procent_taxa_vamala", 0),
                                  corp.get("accize", 0), corp.get("accesorii", 0),
                                  _common.cota_ceruta(corp),
                                  _uc_comun.bifa(corp, "certificat_amanare", False), platitor)
            cont = _cv.cere_cont(conn, schema, corp.get("cont_destinatie"), "cont_destinatie")  # [R54]
            val = Decimal(str(corp["valoare_vamala"]))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        mod_txt = {"decont": "TVA in decont (certificat art. 326(4), 4426=4427)",
                   "vama": "TVA platita in vama (deducere pe DVI art. 299(1)c)",
                   "cost": "neplatitor - TVA in cost"}[r["mod_tva"]]
        # [lotul 13, deficiența 552] documentul e DVI-ul (numărul și data), furnizorul extern e partenerul datoriei (401); baza TVA din vamă e
        # în lei, cum o stabilește DVI-ul (CF art.290 alin.(1): „cursul de schimb valutar se stabilește conform prevederilor europene care
        # reglementează calculul valorii în vamă”), deci nu se recalculează aici la cursul BNR. Accesoriile intră în baza TVA (CF art.289
        # alin.(2)); costul lor intră în stoc prin factura transportatorului, înregistrată separat în Facturi primite (se spune la generare).
        from core import jurnal_api as _j
        doc_dvi = _j.eticheta_document("DVI", str(corp["numar_dvi"]).strip(), corp["data"])
        furnizor = str(corp.get("furnizor_nume") or "").strip()
        descr = (corp.get("descriere") or "Import extracomunitar de la %s" % furnizor) + " - " + doc_dvi + ", " + mod_txt
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
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], document_ref=doc_dvi)[0]
            for d, c, s in linii:
                if c == "401":
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, d, c, s, None, furnizor)
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, d, c, s)
        conn.commit()
    acc = Decimal(str(corp.get("accesorii") or 0))
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "taxa_vamala": str(r["taxa_vamala"]),
            "baza_tva": str(r["baza_tva"]), "tva": str(r["tva"]), "mod_tva": r["mod_tva"],
            "avertisment": ("Accesoriile (%s lei) au intrat în baza TVA din vamă; costul lor intră în stoc prin factura transportatorului — "
                            "înregistreaz-o în Facturi primite." % bani(acc)) if acc > 0 else None})


def export_extracomunitar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/export-extracomunitar`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import import_export as _ie
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("valoare",))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            ok, ment = _ie.valideaza_export(corp.get("tara_client"),
                                            _uc_comun.bifa(corp, "dovada_export", False))
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
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            repo_contabilitate.adauga_linie_client(cur, schema, iid, cont_venit, val)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "mentiune": ment})


def nota_tva_incasare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-tva-incasare`; docstringul ei a ramas in stratul HTTP."""
    from core import cota_tva_incasare as _c295
    from core import tva_incasare as _ti
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        sens = corp.get("sens")
        if sens not in ("incasare", "plata"):
            raise _erori.DateInvalide("sens invalid: încasare sau plată")
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
            _uc_comun._campuri_lipsa(corp, ("data", "suma_incasata", "cota"))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            _al = _c295.alegerea(corp)
            tva = _ti.tva_din_incasare(
                corp["suma_incasata"],
                _common.cota_ceruta({**corp, "data": _al.data_cotei}))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        debit, credit = ("4428", "4427") if sens == "incasare" else ("4426", "4428")
        with conn.cursor() as cur:   # [lotul 13, 541 / 524] nu se exigibilizează mai mult TVA decât e neexigibil pe 4428
            from core import ops_sold as _os
            _os.cere_sold_4428(cur, schema, corp.get("data"), tva, sens, camp="op-suma_incasata")
        # [R151] Descrierea implicita numeste RAMURA aleasa: peste sase luni, cine citeste nota
        # trebuie sa poata reconstitui de ce cota e aia si nu alta. Fraza vine de la regula
        # (`cota_tva_incasare.descrierea`), nu se compune aici. O descriere scrisa de om nu se
        # suprascrie — ea e a lui.
        desc = corp.get("descriere") or (
            "TVA la incasare - exigibilitate la "
            + ("incasare (art. 282)" if sens == "incasare" else "plata furnizor")
            + "; " + _c295.descrierea(_al))
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], desc[:200])[0]   # [430d] sursa operațiunii
            repo_contabilitate.adauga_linie_5(cur, schema, iid, debit, credit, tva)
        conn.commit()
    # [lotul 10, deficiența 428] „Formularul manual rămâne doar pentru cazuri speciale”: încasarea / plata prin bancă sau casă legată de
    # factură mută singură TVA-ul (`tva_incasare.linii_la_incasare`); răspunsul o spune, ca nota manuală să nu-l mute a doua oară
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "tva_exigibil": str(tva), "nota": f"{debit}={credit}",
                                          "avertisment": _c295.AVERTISMENT_CAZ_SPECIAL})


def tva_incasare_neexigibile(tenant_id, la, ctx):
    """[P7 · use-case] Corpul rutei `GET /tenants/{tenant_id}/tva-incasare/neexigibile`. [lotul 10, deficiența 428] „ieșirea din sistem
    face regularizarea”: lista facturilor cu TVA rămas pe 4428 la data ieșirii și ce se întâmplă cu fiecare (CF art.282 alin.(7) lit.b:
    facturile emise înainte de ieșire rămân în sistem). Numai citire — nimic nu se mută în 4427 fără încasare."""
    import datetime as _dt
    from decimal import Decimal as _D
    from core import tva_incasare as _tvi, nomenclator_status_factura as _nsf
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        d = _dt.date.fromisoformat(str(la or "").strip()[:10])
    except ValueError:
        raise _erori.DateInvalide("Data: %r nu e o dată din calendar. Se așteaptă forma AAAA-LL-ZZ." % (la,))
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            facturi = _tvi.neexigibile_la(cur, None, d, _nsf.clauza_sql("f"))
    tot = {k: sum((_D(f["rest_neexigibil"]) for f in facturi if f["directie"] == k), _D(0)) for k in ("emisa", "primita")}
    return {"la": d.isoformat(), "facturi": facturi, "tva_neexigibil_emise": str(tot["emisa"]),
            "tva_nededus_primite": str(tot["primita"])}


def nota_leasing(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-leasing`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 523, comanda Costin 13.1] „bunul primit în leasing financiar (2133 = 167) nu intră în registrul mijloacelor fixe,
    deci nu se amortizează niciodată — lipsește cheltuiala, profitul iese mai mare. Primirea cere datele activului (catalog, durată, metodă)
    și locatorul. Dobânda totală pe 8051 tot cu 891 (507). Rata lunară: […] fără locator (506).” TEMEI: OMFP 1802/2014 pct.215 alin.(1):
    în leasingul financiar „utilizatorul înregistrează bunul primit ca imobilizare” și îl amortizează (pct.238); CF art.28 alin.(16):
    „În cazul contractelor de leasing, se aplică următoarele reguli: a) în cazul leasingului financiar, utilizatorul este tratat din punct
    de vedere fiscal ca proprietar”, deci amortizează. Primirea înscrie bunul în registru (activ la validarea notei, 519), cu codul din
    catalog și durata în plaja lui (HG 2139/2004), metoda și data punerii în funcțiune; locatorul e partenerul rândurilor 167 / 404."""
    from core import leasing as _ls, mf_note as _mfn, extrabilant as _xb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        tip = corp.get("tip")
        mf_reg = None
        locator = None
        try:
            _uc_comun._campuri_lipsa(corp, {"primire": ("valoare_capital", "dobanda_totala", "cont_imobilizare", "denumire", "cod_catalog",
                                                        "dnf_luni", "data_pif", "metoda"),
                                            "rata": ("capital", "cota"), "reziduala": ("valoare_reziduala", "cota"),
                                            "operational": ("chirie", "cota", "cont_cheltuiala")}.get(tip, ()))   # [lotul 11, 440 / A4]
            if tip in ("primire", "rata", "reziduala", "operational"):
                locator = _partener_din_corp(corp.get("locator_cui"), corp.get("locator_nume"), "locator", "locatorul (societatea de leasing)")
            if tip == "primire":
                from core import inventariere as _iv
                ci = _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare")
                _verifica_catalog(corp.get("cod_catalog"), corp.get("dnf_luni"))
                mf_reg = _iv.pregateste_mf_plus(dict(corp, valoare=corp["valoare_capital"], cont_imobilizare=ci,
                                                     cont_amortizare=cont_amortizare_pentru(ci), destinatie_cd=False))
                r = _ls.nota_primire_financiar(corp["valoare_capital"], corp.get("dobanda_totala", 0), ci)
                d0 = "Primire în leasing financiar %s de la %s (%s=167 + D8051 dobânda)" % (corp["denumire"], locator[1], ci)
            elif tip == "rata":
                r = _ls.nota_rata_financiar(corp["capital"], corp.get("dobanda", 0),
                                            corp.get("comision", 0), _common.cota_ceruta(corp))
                d0 = "Rata leasing financiar %s (167/666/628=404 + C8051)" % locator[1]
            elif tip == "reziduala":
                r = _ls.nota_reziduala(corp["valoare_reziduala"], _common.cota_ceruta(corp))
                d0 = "Valoare reziduala leasing %s (167=404, inchide 167)" % locator[1]
            elif tip == "operational":
                r = _ls.nota_rata_operational(corp["chirie"], _common.cota_ceruta(corp),
                                              _cv.cere_cont(conn, schema, corp.get("cont_cheltuiala"), "cont_cheltuiala"))
                d0 = "Rata leasing operational %s (612=401)" % locator[1]
            else:
                raise ValueError(nomenclator_cerut("tip", "primire|rata|reziduala|operational"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 212-217"
        info = {}
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            mid = None
            if mf_reg:   # [523 / 519] bunul intră în registru, activ la validarea notei
                cod = _numar_inventar(cur, schema, corp.get("numar_inventar"))
                try:
                    mid = repo_mijloace_fixe.adauga_cu_reevaluare(cur, schema, cod, mf_reg["denumire"], mf_reg["cont_imobilizare"],
                                                                  mf_reg["cont_amortizare"], mf_reg["valoare"], mf_reg["rezidual"],
                                                                  mf_reg["dnf_luni"], mf_reg["data_pif"], mf_reg["metoda"], False)[0]
                except _chei.CheieDublata as e:
                    raise _erori.DateInvalide(e.detaliu())
                repo_mijloace_fixe.seteaza_cod_catalog_schema(cur, schema, mid, str(corp["cod_catalog"]).strip().rstrip("."))
                repo_mijloace_fixe.in_asteptarea_validarii(cur, schema, mid)
                _mfn.leaga(cur, schema, mid, iid, "intrare")
                info.update(mijloc_fix_id=mid, numar_inventar=cod)
            for dd, cc, ss in r["linii"]:
                if mid and dd.startswith("2"):   # bunul primit, pe activ și cu locatorul (167)
                    _mfn.adauga_linie(cur, schema, iid, dd, cc, ss, mid, locator[0], locator[1])
                elif locator and ({"167", "404", "401"} & {dd, cc}):   # [506] locatorul pe rândurile datoriei
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, locator[0], locator[1])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            for cont, sens, suma in r.get("extrabilant") or []:   # [507] 8051 într-o singură parte, legat de notă
                _xb.scrie(cur, schema, corp["data"], cont, sens, suma, "Dobânda leasingului (%s)" % locator[1], inregistrare_id=iid,
                          mijloc_fix_id=mid)
            if r.get("extrabilant"):
                info["extrabilant"] = [_xb.text(*x) for x in r["extrabilant"]]
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def nota_credit(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-credit`; docstringul ei a ramas in stratul HTTP."""
    from core import credite as _cr, ops_sold as _os
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        tip = corp.get("tip", "lung")
        info = {}
        try:
            _uc_comun._campuri_lipsa(corp, {"primire": ("suma",), "dobanda": ("dobanda",), "restanta": ("suma",),
                                            "garantie": ("suma",)}.get(op, ()))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            if op == "primire":
                r = _cr.nota_primire(corp["suma"], tip)
                d0 = f"Primire credit bancar termen {tip}"
            elif op == "dobanda":
                r = _cr.nota_dobanda_angajata(corp["dobanda"], tip)
                d0 = "Dobanda angajata credit (666=168x/519x)"
            elif op == "plata":
                # [lotul 13, deficiența 524] rata stinge 1621/5191, dobânda 1682/5198: niciuna peste soldul contului ei (note validate).
                # „Dobânda a fost înregistrată deja pe 666” n-o mai spune omul — o stabilește soldul: dobânda angajată (sold creditor
                # 1682/5198) se plătește din cont; fără sold și fără nicio ciornă care l-ar crea, dobânda e cheltuiala lunii (666 = 5121);
                # un sold parțial sau o dobândă rămasă în ciornă se refuză (altfel 666 s-ar înregistra de două ori).
                c_cr = _cr._tip(tip)
                dob = Decimal(str(corp.get("dobanda") or 0))
                with conn.cursor() as cur:
                    _os.cere_sold(cur, schema, c_cr["credit"], corp.get("data"), corp.get("rata") or 0, "creditor", "Plata ratei",
                                  camp="op-rata")
                    angajata = False
                    if dob > 0:
                        disp, _sold, ciorne = _os.disponibil(cur, schema, c_cr["dobanda"], corp.get("data"), "creditor")
                        angajata = disp > 0 or bool(ciorne["creeaza"])
                        if angajata:
                            _os.cere_sold(cur, schema, c_cr["dobanda"], corp.get("data"), dob, "creditor", "Plata dobânzii",
                                          camp="op-dobanda")
                r = _cr.nota_plata(corp.get("rata", 0), corp.get("dobanda", 0),
                                   corp.get("comision", 0), tip, dobanda_angajata=angajata)
                info = {"dobanda_din": ("contul %s (dobânda înregistrată)" % c_cr["dobanda"]) if angajata else "666 (cheltuiala lunii)"} \
                    if dob > 0 else {}
                d0 = "Plata rata/dobanda/comision credit"
            elif op == "restanta":
                with conn.cursor() as cur:   # [524] restanța mută rata din credit pe restant: nu peste soldul creditului
                    _os.cere_sold(cur, schema, _cr._tip(tip)["credit"], corp.get("data"), corp.get("suma") or 0, "creditor",
                                  "Restanța", camp="op-suma")
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
        out = {"linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}
        with conn.cursor() as cur:
            if r["linii"]:
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
                for dd, cc, ss in r["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
                out["inregistrare_id"] = iid
            if r.get("extrabilant"):   # [lotul 13, 507] garanția: numai în afara bilanțului, cu documentul ei
                from core import extrabilant as _xb
                for cont, sens, suma in r["extrabilant"]:
                    _xb.scrie(cur, schema, corp["data"], cont, sens, suma, descr[:200], document=corp.get("descriere"))
                out["extrabilant"] = [_xb.text(*x) for x in r["extrabilant"]]
                out["mesaj"] = "Garanția e înregistrată în afara bilanțului: %s. Nu intră în rândurile notelor." % "; ".join(out["extrabilant"])
        conn.commit()
    return _uc_comun.cu_eticheta(schema, out)


def nota_avans(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-avans`; docstringul ei a ramas in stratul HTTP."""
    from core import avansuri as _av, ops_sold as _os
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        dest = corp.get("destinatie", "stocuri")
        _OPERATII_AVANS = ("avans_platit", "regularizare_platit", "avans_incasat",
                           "regularizare_incasat")
        try:
            # [lotul 3] ORDINEA e reparatia: cota se cerea INAINTE de a se uita la operatie, deci
            # cine uita felul operatiunii — sau il scria gresit — afla despre cotă. Felul intai.
            _uc_comun._campuri_lipsa(corp, ("suma", "cota") if op in _OPERATII_AVANS else ())   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
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
                        "regularizează e cea în vigoare la data livrării, nu la data regularizării "
                        "(art. 291 alin. 6 Cod fiscal).")
                _data_cota = _dl
            cota = _common.cota_ceruta({**corp, "data": _data_cota})
            if op == "avans_platit":
                r = _av.nota_avans_platit(corp["suma"], cota, dest)
                d0 = f"Factura avans furnizor ({r['cont_avans']}+4426=401)"
            elif op == "regularizare_platit":
                with conn.cursor() as cur:   # [lotul 13, 524] regularizarea stinge avansul dat (409x): nu peste soldul lui
                    _os.cere_sold(cur, schema, _av.CONT_AVANS.get(dest, "4091"), corp.get("data"), corp.get("suma") or 0, "debitor",
                                  "Regularizarea avansului plătit", camp="op-suma")
                r = _av.nota_regularizare_avans_platit(corp["suma"], cota, dest)
                d0 = "Regularizare avans furnizor la factura finala"
            elif op == "avans_incasat":
                r = _av.nota_avans_incasat(corp["suma"], cota)
                d0 = "Factura avans client (4111=419+4427)"
            elif op == "regularizare_incasat":
                with conn.cursor() as cur:   # [lotul 13, 524] regularizarea stinge avansul încasat (419): nu peste soldul lui
                    _os.cere_sold(cur, schema, "419", corp.get("data"), corp.get("suma") or 0, "creditor",
                                  "Regularizarea avansului încasat", camp="op-suma")
                r = _av.nota_regularizare_avans_incasat(corp["suma"], cota)
                d0 = "Regularizare avans client la factura finala"
            else:                       # nu se poate ajunge aici: `op` e verificat mai sus
                raise ValueError(nomenclator_cerut("operatie", _OPERATII_AVANS))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 282(2)b CF"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        # [lotul 11, deficiența 440] tipul, durata, câmpurile lipsă, valoarea, CUI-ul și numărul facturii — toate deodată, fiecare lângă
        # câmpul ei din formularul Operațiuni (`op-…`); perioada închisă (mai sus) rămâne refuzul unic de dinainte
        _er = _erori.ErorileFormularului("Achiziția necorporală nu s-a înregistrat")
        tip = corp.get("tip")
        dnf = corp.get("dnf_luni")
        if tip not in TIPURI:
            _er.camp("op-tip", nomenclator_cerut("tip", TIPURI))
        else:
            cont_imo, cont_am, dnf_regula = TIPURI[tip]
            if tip == "software":
                dnf = 36  # art. 28(9): programe informatice = 3 ani, fix
            elif tip == "constituire":
                dnf = min(int(dnf or 60), 60)  # art. 28(11): max 5 ani
            elif not dnf:
                _er.camp("op-dnf_luni", f"Durata normală de funcționare (luni) obligatorie pentru {tip} "
                                        "(durata contractului/de utilizare, art. 28(9))")
        _uc_comun._campuri_lipsa(corp, ("data", "denumire", "valoare", "cota"), er=_er)
        try:
            if corp.get("valoare") not in (None, "") and Decimal(str(corp["valoare"])) <= 0:
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                _er.camp("op-valoare", "Valoarea operațiunii trebuie să fie un număr mai mare decât zero.")
        except ArithmeticError:
            _er.camp("op-valoare", "Valoarea operațiunii trebuie să fie un număr mai mare decât zero.")
        if not furnizor_cui:      # calculat înaintea blocului; validarea rămâne aici
            _er.camp("op-furnizor_cui", "CUI furnizor obligatoriu (achiziția necorporală e factura de la furnizor)")
        if not str(corp.get("numar") or "").strip():
            _er.camp("op-numar", "număr factura furnizor obligatoriu")
        _er.refuza()
        from core import facturi_api as _fa
        try:
            val = Decimal(str(corp["valoare"]))
            cota = _common.cota_ceruta(corp)
            tva = (val * Decimal(str(cota)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            numar = str(corp.get("numar") or "").strip()
            furnizor_nume = str(corp.get("furnizor_nume") or "").strip()
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(str(e) or "valoare invalidă")
        with conn.cursor() as cur:
            # [lotul 10, C73] fără cod scris (ecranul n-are câmpul), codul de inventar e primul liber („NEC-LIC”, „NEC-LIC-2”, …):
            # înainte, a doua licență primea același cod și scrierea cădea cu 500; un cod scris de om și deja folosit -> refuz numit
            try:
                mfid = repo_mijloace_fixe.adauga(cur, schema, corp.get("cod") or repo_mijloace_fixe.cod_liber(cur, schema, f"NEC-{tip[:3].upper()}"),
                                                 corp["denumire"][:200], cont_imo, cont_am, val, int(dnf), corp["data"])[0]
            except _chei.CheieDublata as e:
                raise _erori.DateInvalide(e.detaliu())
            tranzactie.fixeaza_schema(cur, schema)   # creeaza_factura foloseste INSERT necalificat
            # rand FACTURA (achizitie normala de la furnizor RO cu CUI) -> D394 tip A. MF (mijloace_fixe) ramane
            # separat: factura = documentul de achizitie; imobilizarea = activul amortizabil (amortizare/D406).
            # `_tert_pl` s-a înghețat înaintea blocului (TVA deductibilă -> furnizor plătitor)
            try:   # [10.10.2026] refuzul motivat al emiterii ajunge la contabil (422), nu ca 500 (deficiența C7, generalizată)
                fres = _fa.creeaza_factura(conn, numar=numar, data_emitere=corp["data"], directie="primita",
                                           linii=[{"descriere": corp["denumire"][:200], "cantitate": 1,
                                                   "pret_unitar": str(val), "cota_tva": cota}],
                                           tert_nume=furnizor_nume or None, tert_cui=furnizor_cui, status="importata",
                                           tert_platitor_tva=_tert_pl)
            except ValueError as e:
                raise _erori.DateInvalide(str(e))
            fid = fres["factura_id"]
            iid = repo_contabilitate.nota_facturi_cu_factura(cur, schema, corp["data"], fid, f"Achizitie necorporala {tip}: {corp['denumire']}"
                                       f" (amortizare {_common.cate(dnf, 'lună', 'luni')}, art. 28(9) CF)"[:200])[0]
            # [lotul 10, deficiența 428] firma în sistemul TVA la încasare la data facturii: deducerea e amânată până la plată (CF art.297
            # alin.(3)) -> TVA pe 4428, mutat pe 4426 la plată (`tva_incasare.linii_la_incasare`); altfel 4426, ca până acum
            from core import tva_incasare as _tvi
            _cont_tva = "4428" if _tvi.regim(cur, schema, fid) == _tvi.REGIM_INCASARE else "4426"
            # [lotul 13, 519 / 522] activul intră în registru la VALIDAREA notei (`mf_note`, intrare); rândul activului poartă activul
            from core import mf_note as _mfn
            repo_mijloace_fixe.in_asteptarea_validarii(cur, schema, mfid)
            _mfn.leaga(cur, schema, mfid, iid, "intrare")
            _mfn.adauga_linie(cur, schema, iid, cont_imo, "404", val, mfid)
            repo_contabilitate.adauga_linie(cur, schema, iid, _cont_tva, "404", tva)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "factura_id": fid, "mijloc_fix_id": mfid, "dnf_luni": int(dnf),
            "conturi": [cont_imo, cont_am]})


def _cere_amortizarea_inregistrata(conn, schema, cont_amortizare, ref, de_eliminat, denumire, mijloc_fix_id):
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
    from core import reevaluare as _rv, mf_registru as _mfr
    # [lotul 13, deficiențele 516 / 522] „Verificarea citește în 2813 doar notele din 2026 (400) și ignoră soldul de preluare (2.200, lunile
    # 2025); registrul arată corect 2.600.” Amortizarea înregistrată se citește PE ACTIV, cu partea lui din soldul preluat — aceeași cifră ca
    # registrul (`mf_registru.inregistrat_pe_activ`), nu rulajele contului de la 1900 (fără soldul inițial) și nu contul întreg (alte active).
    with conn.cursor() as cur:
        repo_contabilitate.search_path_firma(cur, schema)
        sold = _mfr.inregistrat_pe_activ(cur, schema, repo_mijloace_fixe.toate(cur), mijloc_fix_id, ref)
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie", "reevaluare")
        try:
            _uc_comun._campuri_lipsa(corp, ("suma",) if op == "surplus" else ("mijloc_fix_id", "data", "valoare_justa"))   # [lotul 11, 440 / A4]
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
                den, ci, ca, val, rez, dnf, pif, met, reev, dcd, prel, dprel = mf
                ref = _date.fromisoformat(corp["data"])
                from core import d406_active as _d406
                mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca,
                        "valoare": val, "rezidual": rez, "dnf_luni": dnf, "data_pif": pif,
                        "metoda": met, "reevaluari": reev, "destinatie_cd": dcd,
                        "amortizare_preluata": prel, "data_preluare": dprel}   # [359, A.1]
                amortizare = _d406.amortizat_la_data(mf_d, ref)["amortizat"]   # metoda reala, nu liniar
                from core import amortizare_lunii as _amc
                ci, ca = _amc.conturile_fisei(den, ci, ca, amortizare > 0)   # [C129] fără contul activului nu se scrie nota
                _cere_amortizarea_inregistrata(conn, schema, ca, ref, amortizare, den, corp["mijloc_fix_id"])
                # [lotul 12, C116] rezerva din reevaluare (105) și descreșterea trecută anterior pe cheltuieli (655) ale ACESTUI activ: din
                # reevaluările lui aplicate, când cererea nu le dă (ecranul trimite numai valoarea justă). OMFP 1802/2014 pct.111 alin.(2):
                # descreșterea se tratează „ca o scădere a rezervei din reevaluare […] cu minimul dintre valoarea acelei rezerve și valoarea
                # descreșterii, iar eventuala diferență rămasă neacoperită se înregistrează ca o cheltuială”; alin.(1): creșterea compensează
                # întâi „cheltuiala cu descreșterea recunoscută anterior la acel activ”
                # [lotul 13, 511] formularul nu le mai cere (vin din reevaluările activului); cererea API le poate da pentru o
                # reevaluare dinaintea preluării, care nu e în registrul iConta
                _gol = lambda k: corp.get(k) is None or str(corp.get(k)).strip() == ""   # noqa: E731
                if _gol("sold_105_activ") or _gol("pierdere_655_anterioara"):
                    with conn.cursor() as cur:
                        _s105, _p655 = repo_reevaluari.rezerva_si_pierderea(cur, schema, corp["mijloc_fix_id"])
                s105 = _s105 if _gol("sold_105_activ") else corp["sold_105_activ"]
                p655 = _p655 if _gol("pierdere_655_anterioara") else corp["pierdere_655_anterioara"]
                r = _rv.nota_reevaluare(val, amortizare, corp["valoare_justa"], ci, ca, s105, p655)
                descr = (f"Reevaluare {den}: neta {bani(r['valoare_neta'], 'lei')} -> justa "   # [lotul 10, 430e, clasa]
                         f"{bani(r['valoare_neta'] + r['diferenta'], 'lei')} (OMFP 1802 pct.111-116)")
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
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            from core import mf_note as _mfn
            for dd, cc, ss in r["linii"]:
                if fapt and (dd.startswith("2") or cc.startswith("2")):   # [lotul 13, 522] rândurile activului reevaluat, pe activ
                    _mfn.adauga_linie(cur, schema, iid, dd, cc, ss, fapt["mijloc_fix_id"])
                else:
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
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **extra})


def nota_provizion_ep(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-provizion`; docstringul ei a ramas in stratul HTTP.

    [lotul 13] 511: la ajustarea creanțelor se alege factura neîncasată — suma (soldul ei) și zilele de la scadență le dă aplicația;
    512: nota spune partea deductibilă și pe cea nedeductibilă, iar cea nedeductibilă intră singură în ajustările fiscale ale impozitului
    pe profit (D101 rd.29, „provizioane / ajustări nedeductibile”, legată de notă: în calcul cu nota validată, ștearsă odată cu ea —
    `ajustari_fiscale.adauga`); 513: tipurile 1515 și 1517; 514: contul de ajustare a stocurilor ales din 391–398; 524: reluarea nu poate
    depăși soldul contului de ajustare / provizion. TEMEI: CF art.26 alin.(1) lit.c) („30% din valoarea creanțelor […] neîncasate într-o
    perioadă ce depășește 270 de zile de la termenul de scadență”), lit.j) (100% la falimentul declarat); provizioanele altele decât cele
    din art.26 și ajustările pentru deprecierea stocurilor nu sunt deductibile (art.25 alin.(4) — se adaugă la rezultatul fiscal, rd.29)."""
    from datetime import date as _date
    from core import provizioane as _pv, ops_sold as _os, ajustari_fiscale as _aj
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        # [lotul 13] ajustarea creanțelor: constituirea pe factura aleasă, reluarea pe sumă — două feluri, nu o acțiune ascunsă
        act = {"creanta": "constituire", "creanta_reluare": "reluare"}.get(fel) or corp.get("actiune")
        info = {}
        nedeductibil = Decimal("0")
        try:
            _uc_comun._campuri_lipsa(corp, {"creanta": ("data", "factura_id"), "creanta_reluare": ("data", "suma"),
                                            "provizion": ("data", "actiune", "suma", "tip"),
                                            "stoc": ("data", "actiune", "suma", "cont_ajustare")}.get(fel, ("data", "actiune")))
            data = _date.fromisoformat(str(corp["data"])[:10])
            if fel == "creanta":
                from core import reconciliere_api as _rec
                f = next((x for x in _rec.facturi_deschise_detalii(conn, schema) if x["directie"] == "emisa" and str(x["id"]) == str(corp["factura_id"])), None)
                if not f:
                    raise _erori.DateInvalide({"mesaj": "Alege factura emisă neîncasată din listă.",
                                               "erori_campuri": [{"camp": "op-factura_id", "mesaj": "Alege factura din listă."}]})
                with conn.cursor() as cur:
                    scad = repo_operatiuni.scadente_facturi(cur, schema, [f["id"]]).get(f["id"])
                zile = (data - scad).days if scad else None
                suma = Decimal(str(f["sold"]))
                r = _pv.nota_ajustare_creanta(suma, act)
                pct, temei = _pv.deductibilitate_creanta(zile if zile is not None else 0, _uc_comun.bifa(corp, "garantata", False),
                                                          _uc_comun.bifa(corp, "afiliata", False), _uc_comun.bifa(corp, "faliment", False))
                if zile is None and not _uc_comun.bifa(corp, "faliment", False):
                    temei += " — factura n-are termen de scadență, deci zilele de la scadență nu se pot socoti"
                ded, nedeductibil = _pv.parti_fiscale(suma, pct)
                from core.pdf_util import serie_nr as _serie_nr   # [443] seria și numărul separat, fără seria dublată din număr
                info = {"deductibil_procent": pct, "temei": temei, "zile_de_la_scadenta": zile, "factura": _serie_nr(f.get("serie"), f["numar"]),
                        "deductibil": str(ded), "nedeductibil": str(nedeductibil)}
                d0 = f"Ajustare creanta {f['tert_nume']} {_serie_nr(f.get('serie'), f['numar'])} — deductibil {bani(ded, 'lei')}, nedeductibil {bani(nedeductibil, 'lei')}"
            elif fel == "creanta_reluare":
                with conn.cursor() as cur:
                    _os.cere_sold(cur, schema, "491", data, corp["suma"], "creditor", "Reluarea ajustării", camp="op-suma")
                r = _pv.nota_ajustare_creanta(corp["suma"], act)
                d0 = "Reluare ajustare creante 491=7814"
            elif fel == "provizion":
                if act == "reluare":
                    with conn.cursor() as cur:
                        _os.cere_sold(cur, schema, _pv.PROVIZIOANE.get(corp.get("tip"), "151"), data, corp["suma"], "creditor",
                                      "Reluarea provizionului", camp="op-suma")
                r = _pv.nota_provizion(corp["suma"], corp.get("tip"), act)
                if act == "constituire" and not r["deductibil"]:
                    nedeductibil = Decimal(str(r["linii"][0][2]))
                info = {"deductibil": str(r["linii"][0][2]) if r["deductibil"] else "0.00", "nedeductibil": str(nedeductibil)}
                d0 = f"Provizion {corp.get('tip')} ({act})" + ("" if r["deductibil"] else " - nedeductibil fiscal")
            elif fel == "stoc":
                # [lotul 13, garda conturilor din corp] contul se confruntă cu planul firmei (ca înainte de 504, fără implicitul 397)
                cont = _cv.cere_cont(conn, schema, corp.get("cont_ajustare"), "cont_ajustare")
                if act == "reluare":
                    with conn.cursor() as cur:
                        _os.cere_sold(cur, schema, cont, data, corp["suma"], "creditor", "Reluarea ajustării", camp="op-suma")
                r = _pv.nota_ajustare_stoc(corp["suma"], cont, act)
                if act == "constituire":
                    nedeductibil = Decimal(str(r["linii"][0][2]))
                info = {"deductibil": "0.00", "nedeductibil": str(nedeductibil)}
                d0 = f"Ajustare depreciere stocuri {cont} ({act}) - nedeductibil fiscal"
            else:
                raise ValueError(nomenclator_cerut("fel", "creanta|creanta_reluare|provizion|stoc"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 26 CF / OMFP 1802"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            if nedeductibil > 0:   # [512] partea nedeductibilă -> D101 rd.29, legată de notă
                from core import eticheta_nota as _et
                _aj.adauga(cur, schema, int(str(corp["data"])[:4]), _aj.trimestrul(corp["data"]), "P29", nedeductibil,
                           ("Partea nedeductibilă a notei: %s" % d0)[:500], _et.nota(cur, schema, iid), None, iid)
                info["ajustare_fiscala"] = "Partea nedeductibilă, %s, intră în rezultatul fiscal (D101 rd.29) după validarea notei." % bani(nedeductibil, "lei")
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def _cere_stoc_pe_articol(cur, schema, actiune):
    """[lotul 13, deficiențele 510 / 548 / 551] Operațiunea scoate sau pune bunul în fișa de magazie, deci cere stocul ținut pe articol
    (cantitativ-valoric); la firma fără metodă declarată sau global-valorică — refuzul metodei de stoc, cu butonul spre Date firmă
    (`metoda_stoc.cere`, aceeași regulă ca factura cu marfă și livrarea intracomunitară: 551, „Inconsecvent: vânzarea în regim de marjă și
    cea de aur au trecut fără metoda de stoc”)."""
    from core import metoda_stoc as _ms
    try:
        _ms.cere(cur, schema, _ms.CV, actiune)
    except ValueError as e:
        raise _erori.CerereGresita(_uc_comun.refuz_spre_ecran(str(e), getattr(e, "cod", None), getattr(e, "ecran", None) or "date_firma",
                                                            getattr(e, "regula", None)))


#: conturile de stoc ale bunurilor alese în Operațiuni: produsele finite (345) și mărfurile (371)
_STOC_FEL = {"345": "produs finit (345)", "371": "marfă (371)"}


def _articol_stoc(cur, schema, denumire, cont, camp, um=None, nou=False):
    """[lotul 13, 510 / 548] Articolul de stoc ales în formular (lista „operatiuni-date?ce=articole”): (id, denumire, um). Bunul e pe contul
    cerut (`cont`: 345 produse finite, 371 mărfuri) — altfel refuz lângă câmp. `nou` (obținerea): un produs care nu e încă în stoc se
    creează pe 345 / 711, cu unitatea de măsură cerută (nu se presupune „buc”)."""
    from core import produse_api as _pa, stocuri_cv_api as _cva
    den = " ".join(str(denumire or "").split())

    def refuz(m):
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp, "mesaj": m}]})
    ex = _pa.articol_dupa_denumire(cur, schema, den)
    if ex:
        cs = repo_operatiuni.contul_stocului(cur, schema, ex[0])
        if not cs.startswith(cont):
            refuz("„%s” e în stoc pe contul %s, nu ca %s. Alege bunul din listă." % (ex[1], cs, _STOC_FEL[cont]))
        return ex
    if not nou:
        refuz("„%s” nu e în stoc ca %s. Alege bunul din listă (cele cu stoc)." % (den, _STOC_FEL[cont]))
    if not str(um or "").strip():
        m = "Produsul „%s” e nou în stoc: scrie unitatea lui de măsură (buc, kg, m …)." % den
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-um", "mesaj": m}]})
    return _cva.articol_pentru_intrare(cur, schema, den, str(um).strip(), cont, "711"), den, str(um).strip()


def _cantitate_pozitiva(v, camp):
    from decimal import InvalidOperation
    try:
        c = Decimal(str(v).replace(",", "."))
    except (InvalidOperation, ValueError):
        c = None
    if c is None or c <= 0:
        m = "Cantitatea trebuie să fie un număr mai mare decât zero."
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp, "mesaj": m}]})
    return c


def _iesire_din_stoc(conn, schema, articol, cantitate, data, document):
    """[lotul 13, 548] Ieșirea bunului din stoc, ca orice ieșire pe articol (`stocuri_cv_api.iesire`: CMP, nota ei 607 = 371 cu documentul
    vânzării, fișa de magazie): {"id", "valoare", "inregistrare_id"}; stocul insuficient — refuz lângă cantitate."""
    from core import stocuri_cv_api as _cva
    r = _cva.iesire(conn, schema, {"articol_id": articol[0], "data": data, "cantitate": str(cantitate), "document": document})
    if r is None:
        m = "Bunul ales nu mai e în nomenclatorul de stoc. Alege-l din nou din listă."
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-articol", "mesaj": m}]})
    if r.get("eroare"):
        m = "„%s”: %s" % (articol[1], r["eroare"])
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-cantitate", "mesaj": m}]})
    return r


def _coeficient_348(cur, schema, data):
    """[lotul 13, 510] Coeficientul de repartizare a diferențelor de preț la produse, din evidență — OMFP 1802/2014 pct.286 alin.(4):
    (soldul inițial al diferențelor de preț + diferențele aferente intrărilor, cumulat de la începutul exercițiului) / (soldul inițial al
    stocurilor la preț de înregistrare + valoarea intrărilor la preț de înregistrare, cumulat de la începutul exercițiului). Soldul
    inițial = 348 / 345 la 31.12 al anului trecut (soldurile preluate + notele validate); intrările = rândurile 345 debit ale notelor
    validate din an; diferențele intrărilor = 348 pe notele de obținere (documentul „Bon de predare, transfer, restituire”). Fără nicio
    diferență -> 0 (nimic de repartizat). Numai notele VALIDATE (evidența)."""
    import datetime as _dt
    from core import ops_sold as _os, productie as _pr, documente_interne as _di
    an_inceput = _dt.date(data.year, 1, 1)
    anterior = an_inceput - _dt.timedelta(days=1)
    si_348 = _os.sold_net(cur, schema, "348", anterior)
    si_345 = _os.sold_net(cur, schema, "345", anterior)
    bon = _di.TIPURI["bon_predare"] + "%"
    intrari_345, dif_intrari = (Decimal(str(x)) for x in repo_operatiuni.rulaje_productie_an(cur, schema, bon, an_inceput, data))
    if si_348 + dif_intrari == 0:
        return Decimal("0"), {"sold_initial_348": "0.00", "diferente_intrari": "0.00"}
    try:
        k = _pr.coeficient_348(si_348, dif_intrari, si_345, intrari_345)
    except ValueError as e:
        raise _erori.DateInvalide(str(e) + " Validează întâi notele de obținere a produselor (Bon de predare), apoi vinde.")
    return k, {"sold_initial_348": str(si_348), "diferente_intrari": str(dif_intrari), "sold_initial_345": str(si_345),
               "intrari_345": str(intrari_345)}


def nota_productie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-productie`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 510, comanda Costin 13.1] „Obținerea nu cere produs, cantitate, gestiune; la vânzare costul standard ieșit și
    coeficientul 348 se introduc de mână. Aplicația ține stocul de produse și calculează coeficientul din soldurile 348 și 345.”
    - obținerea: produsul (din stoc sau nou, pe 345 / 711), cantitatea, costul standard unitar și gestiunea; nota 345 = 711 (+ 348 la
      costul efectiv) are documentul „Bon de predare, transfer, restituire” (OMFP 2634/2015, cod 14-3-3A), iar intrarea în fișa de magazie
      e legată de ea (un document cu mișcare de stoc: se respinge din „De validat”, nu se șterge din Registrul jurnal);
    - vânzarea: factura din Facturi emise către client (506: partenerul și documentul), cu produsul din stoc — descărcarea gestiunii
      711 = 345 la ieșire (`descarca_factura`) — și diferențele de preț repartizate asupra ieșirii cu coeficientul din evidență
      (OMFP 1802/2014 pct.286 alin.(4)); nimic din ele nu se mai scrie de mână;
    - producția în curs: neschimbată (331 = 711 / 711 = 331)."""
    from core import productie as _pr
    from core import eticheta_nota as _et_prod
    import datetime as _dt
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        info = {}
        try:
            _uc_comun._campuri_lipsa(corp, {"obtinere": ("produs", "cantitate", "cost_standard", "gestiune"), "pic": ("suma",),
                                            "vanzare": ("produs", "cantitate", "pret_vanzare", "cota")}.get(op, ()))   # [lotul 11, 440 / A4]
            if op not in ("obtinere", "pic", "vanzare"):
                raise ValueError(nomenclator_cerut("operatie", "obtinere|pic|vanzare"))
            data = _dt.date.fromisoformat(str(corp["data"])[:10])
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        if op == "pic":
            try:
                r = _pr.nota_productie_in_curs(corp["suma"], corp.get("moment", "constatare"))
            except ValueError as e:
                raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
            descr = (corp.get("descriere") or f"Productie in curs ({corp.get('moment','constatare')}) 331/711") + " - OMFP 1802"
            with conn.cursor() as cur:
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
                for dd, cc, ss in r["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            conn.commit()
            with conn.cursor() as cur:   # [C201] nota numită pe conexiunea ținută, după commit (nu pe a doua conexiune a lui `cu_eticheta`)
                return _et_prod.in_raspuns(cur, schema, {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})
        cant = _cantitate_pozitiva(corp["cantitate"], "op-cantitate")
        if op == "obtinere":
            from core import stocuri_cv_api as _cva
            with conn.cursor() as cur:
                _cere_stoc_pe_articol(cur, schema, "Obținerea produselor în fișa de magazie")
                art = _articol_stoc(cur, schema, corp["produs"], "345", "op-produs", um=corp.get("um"), nou=True)
            try:
                cs = Decimal(str(corp["cost_standard"]))
                valoare = (cant * cs).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                r = _pr.nota_obtinere(valoare, corp.get("cost_efectiv") or None)
            except (ValueError, ArithmeticError) as e:
                raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
            gestiune = str(corp["gestiune"]).strip()
            descr = (corp.get("descriere") or "Obtinere %s × %s (345=711, cost standard %s)" % (art[1], cant, cs)) + " - OMFP 1802"
            with conn.cursor() as cur:
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], "bon_predare")[0]
                for dd, cc, ss in r["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
                doc = repo_contabilitate.documentul_notei(cur, schema, iid)
            m = _cva.intrare(conn, schema, {"articol_id": art[0], "data": corp["data"], "cantitate": str(cant), "pret_unitar": str(cs),
                                            "document": doc, "locatie": gestiune})
            if m.get("eroare"):
                raise _erori.DateInvalide(m["eroare"])
            with conn.cursor() as cur:   # intrarea în fișă e a notei (documentul cu mișcare de stoc)
                repo_operatiuni.leaga_miscarea_de_nota(cur, schema, m["id"], iid)
            info = {"document": doc, "produs": art[1], "cantitate": str(cant), "gestiune": gestiune, "valoare": str(valoare),
                    "diferenta": ({k: str(v) for k, v in r["diferenta"].items()} if r.get("diferenta") else None)}
            conn.commit()
            with conn.cursor() as cur:   # [C201] ca mai sus
                return _et_prod.in_raspuns(cur, schema, {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})
        # vânzarea: factura către client, descărcarea produsului, diferențele de preț repartizate
        client = _partener_din_corp(corp.get("client_cui"), corp.get("client_nume"), "client", "clientul")
        with conn.cursor() as cur:
            _cere_stoc_pe_articol(cur, schema, "Vânzarea produselor din stoc")
            art = _articol_stoc(cur, schema, corp["produs"], "345", "op-produs")
        try:
            linie = {"descriere": art[1], "um": art[2], "cantitate": str(cant), "pret_unitar": str(corp["pret_vanzare"]),
                     "cota_tva": _common.cota_ceruta(corp), "cont_venit": "701", "articol_id": art[0]}
        except ValueError as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        fid, numar, nid_fact = _emite_catre(conn, schema, corp, client, linie, "Vânzarea produselor")
        from core import stocuri_cv_api as _cva
        d = _cva.descarca_factura(conn, schema, fid, corp["data"])
        if d.get("erori"):
            m = "Vânzarea nu s-a înregistrat: %s — %s. Nimic nu s-a scris." % (art[1], d["erori"][0]["eroare"])
            raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-cantitate", "mesaj": m}]})
        iesit = sum((Decimal(str(x["valoare"])) for x in d["descarcate"]), Decimal("0"))
        with conn.cursor() as cur:
            k, baza = _coeficient_348(cur, schema, data)
            dif = _pr.nota_diferente_iesire(iesit, k)
            nid_dif = None
            if dif["linii"]:
                from core import eticheta_nota as _etn
                doc_f = _etn.factura(cur, schema, fid)
                nid_dif = repo_contabilitate.nota_operatiune_ciorna(
                    cur, schema, corp["data"], ("Diferente de pret repartizate asupra iesirii %s (K = %s, OMFP 1802 pct.286)" % (art[1], k))[:200],
                    document_ref=doc_f)[0]
                for dd, cc, ss in dif["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, nid_dif, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": nid_fact, "factura_id": fid, "numar_factura": numar,
                                          "descarcare": [{k2: str(v) for k2, v in x.items()} for x in d["descarcate"]],
                                          "coeficient_348": str(k), "baza_coeficient": baza, "nota_diferente_id": nid_dif,
                                          "linii": [[a, b, str(c)] for a, b, c in dif["linii"]]})


def _factura_primita_existenta(cur, schema, furnizor_cui, numar):
    """[lotul 13, 506] Factura furnizorului deja în Facturi primite (același furnizor și număr): (id, data) sau None — o operațiune care ar
    înregistra-o a doua oară se leagă de ea."""
    r = repo_operatiuni.factura_primita_dupa_furnizor_si_numar(cur, schema, furnizor_cui, numar)
    return r[:2] if r else None


def _obiect(cur, schema, obiect_id, stare):
    """[lotul 13, 508] Obiectul de inventar ales: (id, denumire, valoare) dacă e în starea cerută — „magazie” (intrat, nedat în folosință)
    sau „folosinta” (dat în folosință prin notă validată, nescos); altfel refuz lângă câmp."""
    o = repo_operatiuni.obiect_inventar(cur, schema, obiect_id)   # (id, denumire, valoare, data_intrare, nota_dare_id, scoatere_id, st_intrare, st_dare, factura_id)
    r = (o[0], o[1], o[2], o[4], o[5], o[6], o[7], o[8]) if o else None
    ok = r is not None and (
        (stare == "magazie" and r[3] is None and r[4] is None and (r[5] == "validata" or r[7] is not None)) or
        (stare == "folosinta" and r[3] is not None and r[6] == "validata" and r[4] is None))
    if not ok:
        m = ("Alege obiectul din lista celor intrate în gestiune și nedate încă în folosință (cu nota intrării validată)." if stare == "magazie"
             else "Alege obiectul din lista celor date în folosință (nota dării validată) și nescoase încă.")
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-obiect_id", "mesaj": m}]})
    return r[0], r[1], r[2]


def nota_obiect_inventar(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-obiect-inventar`; docstringul ei a ramas in stratul HTTP.

    [lotul 13] 505: valoarea e „fără TVA”; 506: achiziția cere furnizorul (din Parteneri / Verifică ANAF) și numărul facturii — documentul
    notei e factura, nu „Notă de calcul”; factura deja în Facturi primite nu se înregistrează a doua oară (obiectul se leagă de ea);
    507: clasa 8 într-o singură parte (D 8035 la dare, C 8035 la scoatere), fără 891 și în afara totalurilor notei (`extrabilant`);
    508: darea și scoaterea aleg obiectul din registrul obiectelor de inventar, iar valoarea vine de la el."""
    from datetime import date as _date
    from core import obiecte_inventar as _oi, extrabilant as _xb
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        obiect = None
        fact_exist = None
        try:
            _uc_comun._campuri_lipsa(corp, {"achizitie": ("data", "denumire", "valoare", "cota", "numar"), "dare_folosinta": ("data", "obiect_id"),
                                            "scoatere": ("data", "obiect_id")}.get(op, ()))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            if op == "achizitie":
                ref = _date.fromisoformat(corp["data"])
                furn = _partener_din_corp(corp.get("furnizor_cui"), corp.get("furnizor_nume"), "furnizor", "furnizorul")
                if not _oi.e_obiect_inventar(corp["valoare"], ref,
                                             _uc_comun.bifa(corp, "durata_sub_1_an", False)):
                    raise ValueError(f"valoarea depășește pragul pentru mijloc fix, de "
                                     f"{bani(_oi.prag_mf(ref), 'lei')} (OUG 8/2026): "
                                     "înregistrează bunul ca mijloc fix")
                r = _oi.nota_achizitie(corp["valoare"], _common.cota_ceruta(corp))
                with conn.cursor() as cur:
                    fact_exist = _factura_primita_existenta(cur, schema, furn[0], corp["numar"])
                d0 = "Achizitie obiect de inventar %s 303+4426=401" % corp["denumire"]
            elif op == "dare_folosinta":
                with conn.cursor() as cur:
                    obiect = _obiect(cur, schema, corp["obiect_id"], "magazie")
                r = _oi.nota_dare_folosinta(obiect[2])
                d0 = "Dare in folosinta %s: 603=303 + D8035" % obiect[1]
            elif op == "scoatere":
                with conn.cursor() as cur:
                    obiect = _obiect(cur, schema, corp["obiect_id"], "folosinta")
                r = _oi.nota_scoatere_uz(obiect[2])
                d0 = "Scoatere din folosinta %s: C8035 (proces-verbal)" % obiect[1]
            else:
                raise ValueError(nomenclator_cerut("operatie", "achizitie|dare_folosinta|scoatere"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 / OUG 8/2026"
        iid = None
        info = {}
        with conn.cursor() as cur:
            if op == "achizitie":
                from core import jurnal_api as _j
                if fact_exist:   # [506] factura e deja în Facturi primite, cu contarea ei: obiectul se leagă de ea, nicio notă nouă
                    info["factura_furnizor"] = "deja în Facturi primite (nr. %s): obiectul se leagă de ea, nu se înregistrează a doua oară" % corp["numar"]
                else:
                    iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200],
                                                                    document_ref=_j.eticheta_document("Factura", corp["numar"], corp["data"]))[0]
                    for dd, cc, ss in r["linii"]:
                        repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, furn[0], furn[1])
                info["obiect_id"] = repo_operatiuni.obiect_inventar_scrie(cur, schema, corp["denumire"][:200], r["linii"][0][2], corp["data"], furn[0],
                                                              furn[1], str(corp["numar"]), iid, fact_exist[0] if fact_exist else None)
            elif op == "dare_folosinta":
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], "bon_consum")[0]
                for dd, cc, ss in r["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
                for cont, sens, suma in r["extrabilant"]:
                    _xb.scrie(cur, schema, corp["data"], cont, sens, suma, "Dare în folosință: %s" % obiect[1], inregistrare_id=iid,
                              obiect_id=obiect[0])
                repo_operatiuni.obiect_dat_in_folosinta(cur, schema, obiect[0], iid)
                info["extrabilant"] = [_xb.text(*x) for x in r["extrabilant"]]
            else:   # scoatere: numai C 8035, cu procesul-verbal; nicio notă (nimic în bilanț)
                from core import documente_interne as _di, jurnal_api as _j
                doc = _j.eticheta_document(_di.TIPURI["pv_scoatere"], _di.urmatorul(conn, schema, "pv_scoatere", corp["data"]), corp["data"])
                for cont, sens, suma in r["extrabilant"]:
                    xid = _xb.scrie(cur, schema, corp["data"], cont, sens, suma, "Scoatere din folosință: %s" % obiect[1], document=doc,
                                    obiect_id=obiect[0])
                repo_operatiuni.obiect_scos_din_folosinta(cur, schema, obiect[0], xid)
                info.update(extrabilant=[_xb.text(*x) for x in r["extrabilant"]], document=doc,
                            mesaj="%s: obiectul «%s» e scos din folosință; în afara bilanțului: %s." % (doc, obiect[1], _xb.text(*r["extrabilant"][0])))
        conn.commit()
    out = {"linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info}
    if iid:
        out["inregistrare_id"] = iid
    return _uc_comun.cu_eticheta(schema, out)


def _refuz_dividend(mesaj, camp=None, ecran=None):
    """[lotul 10, deficiența 430] Refuzul notei de dividende, lângă câmpul vinovat când există unul (`erori_campuri`, id-ul din ecran);
    cel care se repară în alt ecran (asociații, în Date firmă) poartă ținta `ecran` — butonul „Deschide Date firmă” (DS cap.6 v2.74),
    ca afirmație tipată (`refuz_spre_ecran`, decizia 21.08), cu câmpul „+ Asociat” adus în vedere (`COD_ASOCIATI_DE_COMPLETAT`)."""
    if ecran:
        from core.mesaje import COD_ASOCIATI_DE_COMPLETAT
        return _erori.DateInvalide(_uc_comun.refuz_spre_ecran(mesaj, COD_ASOCIATI_DE_COMPLETAT, ecran, "Legea 31/1990 art.67 alin.(2)",
                                                              tip="nota de dividende"))
    return _erori.DateInvalide({"mesaj": mesaj, "erori_campuri": [{"camp": camp, "mesaj": mesaj}]} if camp else mesaj)


def _sursa_profitului(cur, schema, data_hot, brut):
    """[lotul 10, deficiența 430a] Contul din care se distribuie dividendul anual și profitul disponibil în el, la data hotărârii.

    Legea 31/1990 art.67 alin.(3): „Nu se vor putea distribui dividende decât din profituri determinate potrivit legii.” OMFP
    1802/2014, funcțiunea contului 117: „Soldul debitor al contului reprezintă pierderea neacoperită, iar soldul creditor, profitul
    nerepartizat”; funcțiunea contului 457: „În creditul contului 457 [...] se înregistrează: – dividendele datorate
    acționarilor/asociaților din profitul realizat în exercițiile precedente (117).” Sursa = contul care ARE soldul: analiticul 1171
    (profitul nerepartizat) sau, la o balanță preluată fără analitic, sinteticul 117 — atunci nota îl debitează pe el (debitarea lui
    1171 cu sold 0 l-ar fi lăsat debitor, adică pierdere) și avertismentul propune reclasarea 117 = 1171. Disponibilul = soldul
    creditor la data hotărârii (`bilant_api.sold_la`: solduri preluate + note validate) minus dividendele deja propuse din el în note
    nevalidate. Întoarce (cont, afirmatie|None): avertismentul despre sursă e o AFIRMAȚIE TIPATĂ (`fapt`, decizia Costin 21.08.2026 —
    afirmațiile despre datele firmei sunt obiecte), cu textul în `motiv` (ecranul îl arată ca avertisment)."""
    from decimal import Decimal as _D
    from core import bilant_api as _ba, eticheta_nota as _et
    sold = _ba.sold_la(cur, schema, data_hot)
    if sold is None:
        raise _refuz_dividend("Profitul nerepartizat la data hotărârii (%s) nu se cunoaște: data e înaintea soldurilor preluate în "
                              "aplicație. Verifică data hotărârii." % data_ro(data_hot), "op-data_hotarare")

    def creditor(potriveste):
        return sum((c - d for k, (d, c) in sold.items() if potriveste(str(k))), _D("0"))
    solduri = {"1171": creditor(lambda k: k.startswith("1171")), "117": creditor(lambda k: k == "117")}
    rezervat = {}
    for cont, s in solduri.items():
        if s <= 0:
            continue
        nev = repo_contabilitate.dividende_nevalidate_din(cur, schema, cont)
        if cont == "117":   # [lotul 13, 527] dividendele din 117 trec prin reclasificarea 117 = 1171 din aceeași notă
            nev = list(nev) + repo_operatiuni.dividende_117_nevalidate(cur, schema)
        rezervat[cont] = (sum((_D(str(x["suma"])) for x in nev), _D("0")), [x["id"] for x in nev])
        if brut <= s - rezervat[cont][0]:
            if cont == "1171":
                return cont, None
            return cont, _af.afirmatie(
                "fapt", "sursa dividendului",
                "Rezultatul reportat e preluat pe contul sintetic 117 (%s), fără analiticul 1171: nota trece întâi suma dividendului pe "
                "analitic (117 = 1171) și repartizează din 1171 (OMFP 1802/2014, contul 1171)." % bani(s, "lei"),
                unde="contul 117, la %s" % data_ro(data_hot),
                temei_completitudine="soldul la data hotărârii: soldurile preluate și notele validate până la ea")   # citit cu `bilant_api.sold_la`
    parti = ["%s: sold creditor %s" % ("1171" if c == "1171" else "117 (fără analitic)", bani(max(s, _D("0")), "lei"))
             for c, s in solduri.items()]
    for c, (suma, ids) in rezervat.items():
        if suma > 0:
            parti.append("din %s, %s sunt deja propuși ca dividende în %s (%s)" % (
                c, bani(suma, "lei"), "nota nevalidată" if len(ids) == 1 else _common.cate(len(ids), "notă nevalidată", "note nevalidate"),
                _et.lista(cur, schema, ids)))
    m = ("Dividendul brut de %s depășește profitul nerepartizat la %s — %s. Legea 31/1990 art.67 alin.(3): „Nu se vor putea "
         "distribui dividende decât din profituri determinate potrivit legii.”" % (bani(brut, "lei"), data_ro(data_hot), "; ".join(parti)))
    if all(s > 0 for s in solduri.values()):
        m += " Profitul e împărțit între 117 și 1171: reclasifică soldul 117 pe 1171 (nota 117 = 1171), apoi generează din nou."
    s121 = creditor(lambda k: k.startswith("121"))
    if s121 > 0:
        m += (" Profitul anului încheiat e încă în contul 121 (%s): după închiderea anului (121 = 117) devine profit nerepartizat."
              % bani(s121, "lei"))
    raise _refuz_dividend(m, "op-brut")


def _dividend_propus(conn, schema, corp, pentru_nota=True):
    """[lotul 10, deficiența 430 a–c, comanda Costin 20.10.2026] Nota de dividende din datele firmei: asociații și cotele la data
    hotărârii (`asociati` + `asociati_istoric`, structura valabilă la dată — `dividende_curs.structura_la`, aceeași ca în D205),
    contul sursă și profitul disponibil (430a), împărțirea pe asociați cu impozitul pe fiecare (430b, `decontari_asociati`) și
    documentul justificativ (430c): hotărârea adunării generale a asociaților (Legea 31/1990 art.194 alin.(1) lit.a: adunarea
    „să aprobe situația financiară anuală și să stabilească repartizarea profitului net”) sau, la un singur asociat, decizia
    asociatului unic (art.196^1 alin.(1)–(2): „acesta va exercita atribuțiile adunării generale a asociaților” și „va consemna de
    îndată, în scris, orice decizie”). Folosit de nota de dividende și de propunerea afișată înainte de generare
    (`pentru_nota=False`: numărul hotărârii nu se cere încă — tabelul se vede cât timp se completează formularul)."""
    from datetime import date as _date
    import psycopg2.extras as _E
    from core import decontari_asociati as _da, dividende_curs as _dc, repo_d205 as _rd

    def data_din(camp):
        try:
            return _date.fromisoformat(str(corp.get(camp) or "")[:10])
        except ValueError:
            return None
    data_nota, data_hot = data_din("data"), data_din("data_hotarare")
    numar = str(corp.get("numar_hotarare") or "").strip()
    if not numar and pentru_nota:
        raise _refuz_dividend("Scrie numărul hotărârii adunării asociaților (sau al deciziei asociatului unic) care aprobă "
                              "dividendele: e documentul justificativ al notei.", "op-numar_hotarare")
    if data_hot is None:
        raise _refuz_dividend("Scrie data hotărârii care aprobă dividendele: asociații și cotele se iau la data ei.",
                              "op-data_hotarare")
    if data_nota and data_nota < data_hot:
        raise _refuz_dividend("Nota de dividende (%s) nu poate fi înaintea hotărârii care le distribuie (%s)."
                              % (data_ro(data_nota), data_ro(data_hot)), "op-data")
    try:
        brut = _da._d(corp.get("brut"))
    except (ArithmeticError, ValueError):
        brut = None
    if brut is None or brut <= 0:
        raise _refuz_dividend("Dividendul brut trebuie să fie un număr pozitiv.", "op-brut")
    interimar = _uc_comun.bifa(corp, "interimar", False)   # select „0”/„1”: bool("0") ar fi True
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # [lotul 10, prins de e2e 430] apelanții (`dividende_impartire`, `nota_asociati`) țin conexiunea pe `public` (verificarea accesului);
        # SQL-ul asociaților (`repo_d205`) e necalificat — schema firmei se fixează aici, pe tranzacție, nu se presupune
        repo_contabilitate.search_path_firma(cur, schema)
        asoc, istoric = _rd.select_asociati(cur), _rd.select_asociati_istoric(cur)
        structura = _dc.structura_la([(a["nume"], a.get("cnp"), a["cota"]) for a in asoc],
                                     [(r["cnp"], r["nume"], r["cota"], r["valabil_pana_la"]) for r in istoric])(data_hot)
        if not structura:
            raise _refuz_dividend(_da.FARA_ASOCIATI, ecran="date_firma")
        sursa, afirmatie = ("463", None) if interimar else _sursa_profitului(cur, schema, data_hot, brut)
    try:
        r = _da.nota_dividend(brut, data_nota or data_hot, interimar, _uc_comun.bifa(corp, "cu_plata", True),
                              asociati=structura, cont_sursa=sursa)
    except _da.StructuraAsociati as e:   # cotele care nu însumează 100%: se repară în Date firmă → Asociați
        raise _refuz_dividend(str(e), ecran="date_firma")
    except ValueError as e:
        raise _refuz_dividend(str(e))
    fel = "Hotărârea adunării generale a asociaților" if len(r["parti"]) > 1 else "Decizia asociatului unic"
    return {"nota": r, "interimar": interimar, "brut": brut, "cont_sursa": sursa, "afirmatie": afirmatie,
            "document": _jurnal_api.eticheta_document(fel, numar, data_hot), "cota_text": _da.procent_text(r["cota"]),
            "asociati": [{"nume": p["nume"], "cota": _da.procent_text(p["cota"]), "brut": str(p["brut"]),
                          "impozit": str(p["impozit"]), "net": str(p["net"])} for p in r["parti"]]}


def dividende_impartire(tenant_id, corp, ctx):
    """[lotul 10, deficiența 430b] Corpul rutei `GET /tenants/{tenant_id}/dividende-impartire`: tabelul arătat ÎNAINTE de
    generarea notei — asociații la data hotărârii, cota, dividendul brut, impozitul și netul fiecăruia, contul sursă și documentul.
    Nu scrie nimic; aceleași reguli ca nota (`_dividend_propus`)."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        p = _dividend_propus(conn, schema, corp, pentru_nota=False)
    return {"asociati": p["asociati"], "document": p["document"], "cont_sursa": p["cont_sursa"], "cota": p["cota_text"],
            "brut": str(p["brut"]), "impozit": str(p["nota"]["impozit"]), "net": str(p["nota"]["net"]),
            "afirmatie": p["afirmatie"]}   # avertismentul despre sursă, tipat (`_sursa_profitului`); ecranul arată `motiv`


def nota_asociati(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-asociati`; docstringul ei a ramas in stratul HTTP."""
    from core import decontari_asociati as _da, ops_sold as _os
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        info = {}
        div = None   # [lotul 10, deficiența 430] dividendul: împărțit pe asociați, din contul care are profitul, cu hotărârea
        try:
            _uc_comun._campuri_lipsa(corp, ("total_interimar", "dividend_anual") if op == "regularizare" else ())   # [lotul 11, 440 / A4]
            if op == "dividend":
                div = _dividend_propus(conn, schema, corp)
                r = div["nota"]
                info = {"impozit": str(r["impozit"]), "net": str(r["net"]), "cota": div["cota_text"],
                        "asociati": div["asociati"], "document": div["document"], "cont_sursa": div["cont_sursa"]}
                if div["afirmatie"]:
                    info["afirmatie"] = div["afirmatie"]
                # [430e] „brut 10000”, „16.00%” -> sumele cu bani(), cota fără zecimale
                d0 = (f"Dividende {'interimare' if div['interimar'] else 'anuale'} {bani(div['brut'], 'lei')} brut, impozit "
                      f"{div['cota_text']} ({div['document']})")
            elif op == "regularizare":
                r = _da.nota_regularizare_interimar(corp["total_interimar"],
                                                    corp["dividend_anual"], corp.get("impozit_interimar"))
                info = {"exces_de_restituit": str(r["exces_de_restituit"]),
                        "impozit_de_recuperat": str(r["impozit_de_recuperat"]),
                        "net_de_restituit": str(r["net_de_restituit"])}
                d0 = "Regularizare dividende interimare (457=463, OMFP 3067/2018)"
            elif op == "restituire_dividend":
                r = _da.nota_restituire_dividend(corp.get("suma_restituita"))
                d0 = "Restituire dividende interimare încasată (5121=463, OMFP 3067/2018)"
            elif op == "imprumut":
                if corp.get("fel") == "restituire":
                    with conn.cursor() as cur:   # [lotul 13, 524] restituirea stinge datoria către asociați (4551): nu peste soldul ei
                        _os.cere_sold(cur, schema, "4551", corp.get("data"), corp.get("suma") or 0, "creditor",
                                      "Restituirea împrumutului", camp="op-suma")
                r = _da.nota_imprumut_asociat(corp.get("suma", 0),
                                              corp.get("fel", "primire"),
                                              corp.get("dobanda", 0))
                d0 = f"Imprumut asociat 4551 ({corp.get('fel','primire')})"
            else:
                raise ValueError(nomenclator_cerut("operatie", "dividend|regularizare|restituire_dividend|imprumut"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0)
        with conn.cursor() as cur:
            # [430c] documentul notei de dividende e hotărârea adunării / decizia asociatului unic, nu „Notă de calcul”
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200],
                                                            document_ref=div["document"] if div else None)[0]
            if div:   # [430b] câte un rând pe fiecare asociat, cu asociatul ca partener al rândului
                # [lotul 13, deficiența 527] „Profitul nerepartizat al F2 stă pe 117 fără analitic […] nota de dividende debitează 117 deși
                # eticheta spune 1171/457.” Profitul preluat pe sinteticul 117 se reclasifică în aceeași notă pe analiticul lui (117 = 1171,
                # suma dividendului), iar dividendul se repartizează din 1171 — OMFP 1802/2014, contul 1171 „Rezultatul reportat reprezentând
                # profitul nerepartizat sau pierderea neacoperită”.
                reclas = div["cont_sursa"] == "117"
                if reclas:
                    repo_contabilitate.adauga_linie(cur, schema, iid, "117", "1171", div["brut"])
                for p in r["parti"]:
                    for dd, cc, ss in p["linii"]:
                        repo_contabilitate.adauga_linie_partener(cur, schema, iid, "1171" if (reclas and dd == "117") else dd, cc, ss,
                                                                 _cif_partener(p["cnp"]), p["nume"])
            else:
                for dd, cc, ss in r["linii"]:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "data": corp["data"],
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def nota_sponsorizare_ep(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-sponsorizare`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 532, comanda Costin 13.1] „Formularul cere cifra de afaceri și impozitul datorat, dar creditul fiscal nu apare
    nicăieri […] Aplicația calculează plafonul […], arată suma scăzută din impozit […], le duce în D101 și ia singură cifra de afaceri și
    impozitul din contabilitate, la nivelul anului.” CF art.25 alin.(4) lit.i) (forma OUG 115/2023, în vigoare de la 01.01.2024): cei care
    sponsorizează „scad sumele aferente din impozitul pe profit datorat la nivelul valorii minime dintre următoarele: 1. valoarea calculată
    prin aplicarea a 0,75% la cifra de afaceri […]; 2. valoarea reprezentând 20% din impozitul pe profit datorat”, iar către entitățile
    fără scop lucrativ „doar dacă beneficiarul sponsorizării este înscris, la data încheierii contractului, în Registrul entităților”.
    Acum: cheltuiala intră singură în ajustările fiscale ale anului (D101 rd.27, legată de notă), iar D101 scade creditul la nivelul
    anului (`d101.calcul_cu_ajustari`: min(sponsorizarea, plafonul pe cifra de afaceri și impozitul anului)); beneficiarul neînscris ->
    rd.33 (nedeductibilă, fără credit). Nota spune plafonul de acum (0,75% din cifra de afaceri a anului până la data notei). Reportul pe
    7 ani nu mai există în lege (forma de mai sus nu-l are) — se spune, nu se calculează."""
    from core import sponsorizari as _sp, ajustari_fiscale as _aj
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("data", "suma", "mod"))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            beneficiar = _partener_din_corp(corp.get("beneficiar_cui"), corp.get("beneficiar_nume"), "beneficiar", "beneficiarul sponsorizării")
            in_registru = _uc_comun.bifa(corp, "beneficiar_in_registru")
            r = _sp.nota_sponsorizare(corp["suma"], corp.get("mod"))
            an = int(str(corp["data"])[:4])
            with conn.cursor() as cur:
                ca = Decimal(str(repo_operatiuni.venituri_70x(cur, schema, "%d-01-01" % an, str(corp["data"])[:10]) or 0))
            # plafonul pe cifra de afaceri din sursa unică a regulii (`sponsorizari.plafon_credit`, CF art.25 alin.(4) lit.i pct.1)
            from datetime import date as _date
            ziua = _date.fromisoformat(str(corp["data"])[:10])
            plafon_ca = _sp.plafon_credit(ca, 0, la_data=ziua)["limita_ca"]
            info = {"cifra_afaceri_an": str(ca), "plafon_cifra_afaceri": str(plafon_ca), "in_registru": in_registru,
                    "credit": ("Se scade din impozitul pe profit al anului %d cel mult minimul dintre 0,75%% din cifra de afaceri (acum %s lei: "
                               "%s lei) și 20%% din impozitul pe profit datorat — D101 îl calculează la nivelul anului (rd.27 / rd.43.1). "
                               "Restul de plafon se poate redirecționa prin D177; reportul pe ani nu mai există în lege."
                               % (an, bani(ca), bani(plafon_ca))) if in_registru else
                              "Beneficiarul nu e înscris în Registrul entităților: sponsorizarea e numai cheltuială nedeductibilă (D101 rd.33), "
                              "fără credit fiscal (CF art.25 alin.(4) lit.i))."}
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Sponsorizare %s (6582, nedeductibil, credit fiscal art. 25(4)i)" % beneficiar[1])
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                if "401" in (dd, cc):
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, beneficiar[0], beneficiar[1])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            from core import eticheta_nota as _et
            _aj.adauga(cur, schema, an, _aj.trimestrul(corp["data"]), "P27" if in_registru else "P33", r["linii"][0][2],
                       ("Sponsorizare %s (CF art.25 alin.(4) lit.i))" % beneficiar[1])[:500], _et.nota(cur, schema, iid), None, iid)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], "credit_fiscal": info})


def nota_subventie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-subventie`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 528, comanda Costin 13.1] „Subvenția (445 = 4751) nu se leagă de un mijloc fix, iar reluarea la venituri cere
    lunar de mână valoarea activului, subvenția și amortizarea lunii. Subvenția se leagă de activ, iar reluarea (4751 = 7584) se generează
    singură în fiecare lună, odată cu amortizarea lui.” TEMEI: OMFP 1802/2014 pct.400 alin.(2): subvențiile pentru active „se recunosc […]
    ca venituri […] pe măsura înregistrării cheltuielilor cu amortizarea” activului finanțat. Subvenția pentru investiții se înregistrează
    acum pe activul ales din registru (rândul 445 = 4751 îl poartă); reluarea lunii o scrie „Generează amortizarea”
    (`_reluare_subventii`), proporțional cu amortizarea activului. Formularul manual al reluării a ieșit."""
    from core import subventii as _sb, mf_note as _mfn
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        info = {}
        mid = None
        try:
            _uc_comun._campuri_lipsa(corp, {"exploatare": ("suma", "moment", "cont_venit"), "investitii": ("suma", "moment", "mijloc_fix_id")
                                            }.get(fel, ()))   # [lotul 11, 440 / A4]
            if fel == "exploatare":
                r = _sb.nota_subventie_exploatare(corp["suma"], corp.get("moment"),
                                                  _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit"))
                d0 = f"Subventie exploatare ({corp.get('moment')})"
            elif fel == "investitii":
                mid = int(corp["mijloc_fix_id"])
                with conn.cursor() as cur:
                    if not repo_mijloace_fixe.e_activ(cur, schema, mid):   # activul finanțat, din registru
                        raise _erori.DateInvalide({"mesaj": "Alege mijlocul fix finanțat din registrul activelor.",
                                                   "erori_campuri": [{"camp": "op-mijloc_fix_id", "mesaj": "Alege mijlocul fix din listă."}]})
                r = _sb.nota_subventie_investitii(corp["suma"], corp.get("moment"))
                d0 = f"Subventie investitii 4751 ({corp.get('moment')})"
                info["reluare"] = "Reluarea la venituri (4751 = 7584) se generează odată cu amortizarea lunară a activului."
            else:
                raise ValueError(nomenclator_cerut("fel", "exploatare|investitii"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 1802 pct. 392-402"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                if mid and "4751" in (dd, cc):   # [528] subvenția stă pe activul finanțat
                    _mfn.adauga_linie(cur, schema, iid, dd, cc, ss, mid)
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def _reluare_subventii(cur, schema, an, luna, linii_amortizare):
    """[lotul 13, 528] Reluarea lunii la venituri a subvențiilor pentru investiții: pentru fiecare activ cu subvenție VALIDATĂ pe el (445 =
    4751 cu activul), 4751 = 7584 = amortizarea lunii × subvenție / valoarea activului (OMFP 1802/2014 pct.400 alin.(2); `subventii.
    reluare_lunara_investitii`), cel mult cât a rămas nereluat. Scrie (sau înlocuiește, dacă e ciornă) nota „SUBV-AAAA-LL”; nimic dacă
    nu e nicio subvenție sau dacă nota lunii e deja validată. Întoarce eticheta notei sau None."""
    from decimal import Decimal as _D
    from core import subventii as _sb, mf_note as _mfn, eticheta_nota as _et
    subv = {k: (_D(str(a)), _D(str(b))) for k, (a, b) in repo_operatiuni.subventii_pe_activ(cur, schema).items()}
    numar = "SUBV-%d-%02d" % (int(an), int(luna))
    ex = repo_operatiuni.nota_dupa_numar(cur, schema, numar)
    if ex and ex[1] == "validata":
        return None
    if ex:
        repo_operatiuni.sterge_nota(cur, schema, ex[0])
    rand = []
    for cont_am, rata, den, mid in linii_amortizare:
        if mid not in subv:
            continue
        val = repo_mijloace_fixe.valoarea(cur, schema, mid)
        try:
            suma = _sb.reluare_lunara_investitii(val, subv[mid][0], rata)["reluare"]
        except ValueError:
            continue
        suma = min(suma, subv[mid][0] - subv[mid][1])
        if suma > 0:
            rand.append((mid, den, suma))
    if not rand:
        return None
    # numărul intră la INSERT (sursa „amortizare”, ca tabloul lunii) — nu printr-un UPDATE pe o coloană de cheie unică (C73)
    iid = repo_contabilitate.nota_amortizare_ciorna(cur, schema, _uc_comun.ultima_zi_a_lunii(an, luna), numar,
                                                    "Reluare subvenții pentru investiții %02d/%d (4751=7584, odată cu amortizarea)" % (luna, an))[0]
    for mid, den, suma in rand:
        _mfn.adauga_linie(cur, schema, iid, "4751", "7584", suma, mid)
    return _et.nota(cur, schema, iid)


def _partener_din_corp(cui, nume, cheie, eticheta):
    """[lotul 13, deficiențele 506 / 633] Partenerul operațiunii (câmpurile `op-<cheie>_cui`, `op-<cheie>_nume`), ales în formular din
    Parteneri sau cu „Verifică” la ANAF: (cui în forma păstrată, nume) sau refuz lângă câmp. „Nota nu are partener (401 fără furnizor,
    4111 fără client)”. Valorile se citesc în ruta care le cere (`corp.get("<cheie>_cui")`), ca scanerul formularelor să le vadă."""
    from core import compensari_api as _cz
    cui, nume = str(cui or "").strip(), str(nume or "").strip()
    er = _erori.ErorileFormularului("Nota nu s-a generat")
    if not cui:
        er.camp("op-%s_cui" % cheie, "Alege %s din Parteneri sau scrie CUI-ul și apasă „Verifică”." % eticheta)
    if not nume:
        er.camp("op-%s_nume" % cheie, "Denumirea %s (o aduce „Verifică” de la ANAF)." % eticheta)
    er.refuza()
    return _cz.cui_partener(cui) or cui, nume


def _emite_catre(conn, schema, corp, client, linie, ce):
    """[lotul 13, 506 / 530 / 531] Factura emisă către partener (chiria, refacturarea): documentul justificativ e factura din Facturi emise,
    cu numărul seriei firmei, iar nota e contarea ei de la emitere (o singură notă pe factură). Întoarce (factura_id, numar, nota_id)."""
    from core import facturi_api as _fa
    with conn.cursor() as cur:
        tranzactie.fixeaza_schema(cur, schema)   # emite_factura folosește INSERT necalificat
    try:
        fres = _fa.emite_factura(conn, linii=[linie], tert_nume=client[1], tert_cui=client[0], data_emitere=corp["data"],
                                 platitor_tva=_uc_comun._platitor_tva_firma(conn))
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    iid = (fres.get("contare") or {}).get("inregistrare_id")
    if not iid:
        raise _erori.DateInvalide("%s nu s-a înregistrat: nota contabilă a facturii nu s-a putut scrie (%s). Nimic nu s-a scris."
                                  % (ce, ((fres.get("contare") or {}).get("afirmatie") or {}).get("motiv") or "contarea facturii lipsește"))
    return fres["factura_id"], fres.get("numar"), iid


def nota_chirie(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-chirie`; docstringul ei a ramas in stratul HTTP.

    [lotul 13] 530: refacturarea = factura furnizorului întreagă ca achiziție proprie (605 + 4426 = 401, cu furnizorul) și factura către
    chiriaș din Facturi emise (4111 = 708 + 4427), fără 461 (CF art.271 alin.(2) lit.c)); dacă factura furnizorului e deja în Facturi primite
    (același furnizor și număr), nu se înregistrează a doua oară. 531: chiria încasată e factura către chiriaș; închirierea unui bun imobil e
    scutită fără drept de deducere (CF art.292 alin.(2) lit.e)), afară de opțiunea de taxare notificată (art.292 alin.(3)) — rândul ei
    în D300 (rd.15) vine din categoria liniei. 506: partenerul (furnizor, chiriaș, proprietar) e cerut. 529: răspunsul numește nota."""
    from core import comodat_chirii as _cc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        note = []  # [(descriere, linii, partener (cui, nume) | None)]
        info = {}
        emitere = None
        try:
            _uc_comun._campuri_lipsa(corp, {"comodat": ("valoare",), "chirie_platita": ("chirie", "proprietar"),
                                            "chirie_incasata": ("chirie", "tip_bun"),
                                            "refacturare": ("total_factura", "parte_refacturata", "cota", "numar")}.get(fel, ()))
            if fel == "comodat":   # [lotul 13, 507] numai în afara bilanțului (D / C 8038), fără notă
                r = _cc.nota_comodat(corp["valoare"], corp.get("moment", "primire"))
                emitere = None
                info["extrabilant_comodat"] = r["extrabilant"]
            elif fel == "chirie_platita":
                furn = _partener_din_corp(corp.get("furnizor_cui"), corp.get("furnizor_nume"), "furnizor", "proprietarul")
                cota = _common.cota_ceruta(corp) if corp.get("proprietar") != "pf" else None
                from datetime import date as _date
                r = _cc.nota_chirie_platita(corp["chirie"], cota, corp.get("proprietar", "pj"),
                                            la_data=_date.fromisoformat(str(corp["data"])[:10]) if corp.get("data") else None)
                info = {"nota": r.get("nota", "")} if r.get("nota") else {}
                note.append((f"Chirie platita {furn[1]}", r["linii"], furn))
            elif fel == "chirie_incasata":
                client = _partener_din_corp(corp.get("client_cui"), corp.get("client_nume"), "client", "chiriașul")
                imobil = corp.get("tip_bun") == "imobil"
                taxare = _uc_comun.bifa(corp, "optiune_taxare") if imobil else True
                linie = {"descriere": (corp.get("descriere") or "Chirie")[:200], "cantitate": 1, "pret_unitar": str(corp["chirie"]),
                         "cont_venit": "706"}
                if taxare:
                    linie["cota_tva"] = _common.cota_ceruta(corp)
                else:   # CF art.292 alin.(2) lit.e): închirierea de bunuri imobile, scutită fără drept de deducere
                    linie.update(cota_tva=0, categorie_tva="scutit_fara_drept")
                emitere = ("Chiria", client, linie)
                info["regim"] = ("taxabilă (opțiune de taxare, art. 292 alin. (3))" if imobil else "taxabilă") if taxare else \
                    "scutită fără drept de deducere (art. 292 alin. (2) lit. e)) — D300 rd.15; TVA-ul achizițiilor legate de ea nu se deduce"
            elif fel == "refacturare":
                furn = _partener_din_corp(corp.get("furnizor_cui"), corp.get("furnizor_nume"), "furnizor", "furnizorul utilităților")
                client = _partener_din_corp(corp.get("client_cui"), corp.get("client_nume"), "client", "chiriașul")
                cota = _common.cota_ceruta(corp)
                r = _cc.nota_refacturare(corp["total_factura"], corp["parte_refacturata"], cota)
                info = {"tva_refacturat": str(r["tva_refacturat"])}
                with conn.cursor() as cur:   # [506] factura furnizorului deja în Facturi primite: nu se înregistrează a doua oară
                    dubla = _factura_primita_existenta(cur, schema, furn[0], corp["numar"])
                if dubla:
                    info["factura_furnizor"] = "deja în Facturi primite (nr. %s): nu se înregistrează a doua oară" % corp["numar"]
                else:
                    note.append((f"Factura utilitati {corp['numar']} {furn[1]} - achizitie proprie (art. 271)", r["primire"], furn))
                emitere = ("Refacturarea", client, {"descriere": (corp.get("descriere") or "Refacturare utilități")[:200], "cantitate": 1,
                                                    "pret_unitar": str(r["emitere"][0][2]), "cota_tva": cota, "cont_venit": "708"})
            else:
                raise ValueError(nomenclator_cerut("fel", "comodat|chirie_platita|chirie_incasata|refacturare"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        ids = []
        with conn.cursor() as cur:
            for d0, linii, part in note:
                descr = (corp.get("descriere") or d0)
                iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
                ids.append(iid)
                for dd, cc, ss in linii:
                    if part and ("401" in (dd, cc) or "462" in (dd, cc)):
                        repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, part[0], part[1])
                    else:
                        repo_contabilitate.adauga_linie_2(cur, schema, iid, dd, cc, ss)
        if info.get("extrabilant_comodat"):
            from core import extrabilant as _xb
            with conn.cursor() as cur:
                for cont, sens, suma in info.pop("extrabilant_comodat"):
                    _xb.scrie(cur, schema, corp["data"], cont, sens, suma, (corp.get("descriere") or "Comodat (art. 2146 Cod civil)")[:200],
                              document=corp.get("descriere"))
                    info.setdefault("extrabilant", []).append(_xb.text(cont, sens, suma))
            info["extrabilant_text"] = "Bunul în comodat e înregistrat în afara bilanțului: %s. Nu intră în rândurile notelor." % "; ".join(info["extrabilant"])
        if emitere:
            fid, nr, iid = _emite_catre(conn, schema, corp, emitere[1], emitere[2], emitere[0])
            ids.append(iid)
            info.update(factura_id=fid, factura_numar=nr)
        conn.commit()
    # cheile răspunsului scrise pe nume (nu `**info`): garda „ecranul citește numai ce întoarce ruta” (`test_raspuns_citit`) le vede
    return _uc_comun.cu_eticheta(schema, {"inregistrari": ids, "nota": info.get("nota"), "regim": info.get("regim"),
                                          "tva_refacturat": info.get("tva_refacturat"), "factura_furnizor": info.get("factura_furnizor"),
                                          "extrabilant": info.get("extrabilant"), "extrabilant_text": info.get("extrabilant_text"),
                                          "factura_id": info.get("factura_id"), "factura_numar": info.get("factura_numar")})


def _salariat_decont(cur, schema, salariat_id, data):
    """[lotul 13, deficiența 670 (a)] Salariatul decontului, ales din salariații firmei: {id, nume, cif} sau refuz lângă câmp
    (`op-salariat_id`). Verificarea e în `core.salariat_decont.alege`, comună cu Casa (683)."""
    from core import salariat_decont as _sd
    return _sd.alege(cur, schema, salariat_id, data, "op-salariat_id")


def _plafon_diurnei(conn, cur, schema, corp, data, diurna, sal):
    """[lotul 13, deficiența 670 (b)] Diurna decontului față de plafonul neimpozabil — CF art.76 alin.(2) lit.k, verbatim:
    „… pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit pentru
    indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază
    corespunzătoare locului de muncă ocupat; (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă, prin hotărâre a
    Guvernului, pentru personalul român trimis în străinătate […]. Plafonul aferent valorii a 3 salarii de bază […] se calculează
    distinct pentru fiecare lună în parte, prin raportarea celor 3 salarii la numărul de zile lucrătoare din luna respectivă”.
    Indemnizația internă: 23 lei/zi (Ordinul MF 1235/2023, MO 261/29.03.2023, de la 01.04.2023, actualizând HG 714/2018); externă:
    nomenclatorul HG 518/1995, pe țară, în valută (se scrie din anexă), la cursul BNR al zilei (CF art.290 alin.(2)).
    INTERPRETARE: deplasarea se socotește în luna decontului (zilele lucrătoare și salariul de bază ale lunii lui); o deplasare peste
    două luni se decontează pe fiecare lună. {zile, deplasare, plafon_zi, neimpozabil, impozabil, salariu_baza, zile_lucratoare, curs?}."""
    from core import deconturi as _dp, salariu_istoric as _si, scadente as _sc
    er = _erori.ErorileFormularului("Decontul nu s-a generat")
    dep = corp.get("deplasare")
    if dep not in ("interna", "externa"):
        er.camp("op-deplasare", "Alege deplasarea: în țară sau în străinătate (plafonul neimpozabil al diurnei diferă).")
    try:
        zile = int(str(corp.get("zile") or "").strip())
    except ValueError:
        zile = 0
    if zile <= 0:
        er.camp("op-zile", "Scrie numărul de zile de deplasare (un număr întreg pozitiv).")
    if dep == "externa":
        if not str(corp.get("diurna_bugetara") or "").strip():
            er.camp("op-diurna_bugetara", "Scrie diurna pe zi a țării din anexa HG 518/1995 (în valuta ei).")
        if not str(corp.get("moneda") or "").strip():
            er.camp("op-moneda", "Alege moneda diurnei din HG 518/1995.")
    er.refuza()
    sb = _si.salariu_la(cur, schema, sal["id"], data)
    if sb is None or Decimal(str(sb)) <= 0:
        raise _erori.DateInvalide({"mesaj": "%s n-are salariul de bază în fișă la %s: plafonul neimpozabil al diurnei se limitează la 3 "
                                            "salarii de bază pe lună (CF art.76 alin.(2) lit.k). Completează salariul din Salarizare."
                                            % (sal["nume"], data_ro(data)),
                                   "erori_campuri": [{"camp": "op-salariat_id", "mesaj": "Salariatul n-are salariul de bază în fișă."}]})
    zl = _sc.zile_lucratoare_luna(data.year, data.month)
    curs = Decimal("1")
    bug = None
    if dep == "externa":
        from core import curs_bnr as _cb
        try:
            curs, _dc, _s = _cb.curs_pentru(conn, str(corp["moneda"]).upper(), data)
        except _cb.MonedaNecotata as e:
            raise _erori.DateInvalide({"mesaj": str(e), "erori_campuri": [{"camp": "op-moneda", "mesaj": str(e)}]})
        except _cb.CursIndisponibil as e:
            raise _erori.Conflict(str(e))
        bug = corp["diurna_bugetara"]
    d = Decimal(str(diurna)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    p = _dp.plafon_diurna((d / zile).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), zile, sb, zl, bug, curs, la_data=data)
    neimp = min(d, (p["plafon_zi"] * zile).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    out = {"zile": zile, "deplasare": dep, "plafon_zi": p["plafon_zi"], "neimpozabil": neimp, "impozabil": d - neimp,
           "salariu_baza": Decimal(str(sb)), "zile_lucratoare": zl}
    if dep == "externa":
        out["curs"] = curs
    return out


def nota_decont_deplasare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-decont-deplasare`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 670, comanda Costin 13.1] Proba lui Costin: decont final, casa, avans 1.000, diurnă 300, transport 200, cazare
    400, cota 21% -> 625 = 542 900; 4426 = 542 126; 542 = 5311 26. Reparat: (a) salariatul, ales din salariații firmei, e partenerul
    rândurilor 542 (542 urmărit pe persoană); (b) diurna cu zilele și deplasarea (în țară / în străinătate): partea peste plafonul
    neimpozabil (CF art.76 alin.(2) lit.k) e venit de natură salarială și pleacă spre statul de plată al lunii
    (`diurna_salariat.adauga_excedent`, modulul salarizării), unde intră în impozit, contribuții și D112; (c) transportul și cazarea,
    fiecare cu cota ei, pe baza fără TVA, diurna fără TVA (`deconturi.nota_decont`); (d) nicio cotă precompletată, transportul și
    cazarea opționale; avansul nu poate depăși soldul 542 (deficiența 524, `ops_sold`)."""
    from datetime import date as _date
    from core import deconturi as _dp, ops_sold as _os
    fel = corp.get("fel")
    if fel == "decont" and corp.get("deplasare") == "externa" and corp.get("moneda"):
        _uc_comun._preincalzeste_cursul(corp.get("moneda"), corp.get("data"))   # [P5 val 3] descărcarea BNR, înainte de tranzacție
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        info = {}
        plafon = None
        try:
            _uc_comun._campuri_lipsa(corp, {"avans": ("data", "suma", "sursa"), "decont": ("data", "sursa", "diurna")}.get(fel, ("data",)))
            if fel not in ("avans", "decont"):
                raise ValueError(nomenclator_cerut("fel", "avans|decont"))
            data = _date.fromisoformat(str(corp["data"])[:10])
            with conn.cursor() as cur:
                sal = _salariat_decont(cur, schema, corp.get("salariat_id"), data)
            if fel == "avans":
                r = _dp.nota_avans(corp["suma"], corp.get("sursa"))
                d0 = "Avans spre decontare 542 — %s" % sal["nume"]
            else:
                cote, er = {}, _erori.ErorileFormularului("Decontul nu s-a generat")
                for k, baza, ce in (("cota_transport", corp.get("transport"), "transportului"), ("cota_cazare", corp.get("cazare"), "cazării")):
                    if Decimal(str(baza or 0)) > 0:   # [670 c-d] cota se cere numai pentru cheltuiala care există
                        if corp.get(k) in (None, ""):
                            er.camp("op-" + k, "Alege cota de TVA a %s (0 dacă documentul nu are TVA deductibilă)." % ce)
                        else:
                            cote[k] = _common.cota_ceruta({"cota": corp.get(k), "data": corp.get("data")})
                er.refuza()
                r = _dp.nota_decont(corp.get("avans") or 0, corp.get("diurna") or 0, corp.get("transport") or 0, corp.get("cazare") or 0,
                                    cote.get("cota_transport"), cote.get("cota_cazare"), corp.get("sursa"))
                with conn.cursor() as cur:
                    # [524] avansul decontat stinge 542: nu poate depăși soldul lui (note validate)
                    _os.cere_sold(cur, schema, "542", data, corp.get("avans") or 0, "debitor", "Decontul avansului",
                                  camp="op-avans")
                    plafon = _plafon_diurnei(conn, cur, schema, corp, data, Decimal(str(corp.get("diurna") or 0)), sal) \
                        if Decimal(str(corp.get("diurna") or 0)) > 0 else None
                info = {"total_cheltuieli": str(r["total_cheltuieli"]), "diferenta": str(r["diferenta"]),
                        "tva_transport": str(r["tva_transport"]), "tva_cazare": str(r["tva_cazare"])}
                if plafon:
                    info["diurna"] = {k: str(v) if isinstance(v, Decimal) else v for k, v in plafon.items()}
                d0 = "Decont deplasare %s — %s" % (sal["nume"], "ordin de deplasare și justificative")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - art. 76(2)k CF"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                if "542" in (dd, cc):   # [670 a] 542 pe persoană
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, sal["cif"], sal["nume"])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
            if plafon and plafon["impozabil"] > 0:
                # [670 b] excedentul diurnei = venit de natură salarial (CF art.76 alin.(2) lit.k) -> statul de plată al lunii decontului;
                # [684] excedentul e legat de nota decontului (`nota_id`): ștergerea notei, pe orice drum, îl scoate (cheia străină,
                # ON DELETE CASCADE — `diurna_salariat.DDL_NOTA`)
                from core import diurna_salariat as _ds
                _ds.adauga_excedent(cur, schema, sal["id"], data.year, data.month, plafon["impozabil"], "decont-deplasare:%d" % iid,
                                    "Diurnă peste plafonul neimpozabil, %s (%s, %s)" % (
                                        sal["nume"], "în țară" if plafon["deplasare"] == "interna" else "în străinătate",
                                        _common.cate(plafon["zile"], "zi", "zile")), nota_id=iid)
                info["excedent_in_stat"] = "%02d/%d" % (data.month, data.year)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "salariat": sal["nume"],
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def nota_bacsis(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-bacsis`; docstringul ei a ramas in stratul HTTP."""
    from core import bacsis as _bc
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        fel = corp.get("fel")
        info = {}
        try:
            _uc_comun._campuri_lipsa(corp, {"incasare": ("suma",), "distribuire": ("suma", "data")}.get(fel, ()))   # [lotul 11, 440 / A4]
            if fel == "incasare":
                r = _bc.nota_incasare(corp["suma"], corp.get("sursa", "card"))
                d0 = "Bacsis incasat pe bon fiscal (461=462, fara TVA)"
            elif fel == "distribuire":
                r = _bc.nota_distribuire(corp["suma"], corp["data"], corp.get("sursa", "banca"))
                info = {"impozit": str(r["impozit"]), "net": str(r["net"])}
                d0 = "Distribuire bacsis salariati (impozit %s%% retinut, 462=446)" % r["cota"]
            else:
                raise ValueError(nomenclator_cerut("fel", "incasare|distribuire"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - Legea 376/2022"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]], **info})


def nota_sgr(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-sgr`; docstringul ei a ramas in stratul HTTP."""
    from core import sgr as _sg
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        try:
            _uc_comun._campuri_lipsa(corp, {"virare": ("suma",), "autofactura": ("cota",)}.get(op, ()))   # [lotul 11, 440 / A4]
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
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})


def nota_perisabilitati(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-perisabilitati`; docstringul ei a ramas in stratul HTTP."""
    from core import perisabilitati as _pe
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("valoare_intrari", "procent_limita", "pierdere_constatata", "cota"))   # [lotul 11, 440 / A4]
            r = _pe.calcul(corp["valoare_intrari"], corp["procent_limita"],
                           corp["pierdere_constatata"], _common.cota_ceruta(corp),
                           _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc", "371"),
                           _uc_comun.bifa(corp, "degradare_dovedita_distrusa", False))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or
                 f"Perisabilitati: limita {bani(r['limita'], 'lei')}, deductibil {bani(r['deductibil'], 'lei')}, "
                 f"nedeductibil {bani(r['nedeductibil'], 'lei')} (PV inventariere)")[:200]   # [lotul 10, 430e, clasa] sume cu bani()
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr + " - HG 831/2004")[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "limita": str(r["limita"]),
            "deductibil": str(r["deductibil"]), "nedeductibil": str(r["nedeductibil"]),
            "ajustare_tva": str(r["ajustare_tva"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})


def nota_contract_special(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-contract-special`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_speciale as _cs
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("brut",))   # [lotul 11, 440 / A4]
            r = _cs.nota(corp["brut"], corp.get("fel", "zilier"),
                         corp.get("sursa", "casa"), la_data=corp.get("data"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        fel = corp.get("fel", "zilier")
        descr = (corp.get("descriere") or
                 f"Remuneratie {fel} brut {bani(r['brut'], 'lei')} (net {bani(r['net'], 'lei')})") +                 (" - L52/2011" if fel == "zilier" else " - art. 76(2)g/i CF")   # [lotul 10, 430e, clasa]
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "brut": str(r["brut"]), "cas": str(r["cas"]),
            "cass": str(r["cass"]), "impozit": str(r["impozit"]), "net": str(r["net"]),
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})


def tenant_mijloace_fixe(tenant_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/mijloace-fixe`; docstringul ei a ramas in stratul HTTP."""
    from core import inchidere_luna as _il
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    azi = _common.azi_ro()   # [Retest 2 pct.5] ziua României, ca `ultima_zi_incheiata`
    # [08.10.2026, decizia Costin W2] registrul arată amortizarea ÎNREGISTRATĂ (contul de amortizare), separat de cea teoretică
    # (metoda reală, CF art.28 — `d406_active`), diferența, lunile neînregistrate, durata, codul din catalog și planul lunar
    from core import mf_registru as _mfr
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            rows = repo_mijloace_fixe.toate(cur)
            out = _mfr.registru(cur, rows, azi)
    pana = _il.ultima_zi_incheiata(azi)   # [Retest 2 pct.5] ecranul spune până la ce lună e calculul
    return {"mijloace": out, "calculat_pana_la": "%02d/%d" % (pana.month, pana.year)}


def mijloc_fix_destinatie_cd(tenant_id, mijloc_id, corp, ctx):
    """[lot 19 d11] Bifa «Destinat C&D» pe un activ din registru (CF art.20 alin.(1) lit.b), art.20^1 alin.(8)): cu
    ea, accelerata e permisa si pe conturile din afara lui 2131 (d406_active._metode_permise)."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        valoare = _uc_comun.bifa(corp, "destinatie_cd")
    except (ValueError, KeyError) as e:
        raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            # [08.10.2026, decizia Costin W4] cere «Poate valida» (garda rutei); schimbarea se jurnalizează
            r = repo_mijloace_fixe.seteaza_destinatie_cd(cur, schema, mijloc_id, valoare, ctx.get("uid"))
        if not r:
            raise _erori.Inexistent("Mijlocul fix ales nu există în registrul firmei sau a fost casat.")
        conn.commit()
    return {"id": mijloc_id, "destinatie_cd": valoare, "schimbat": r[1] != valoare}


def mijloc_fix_cod_catalog(tenant_id, mijloc_id, corp, ctx):
    """[08.10.2026, decizia Costin W2] Codul de clasificare din Catalogul HG 2139/2004 („Registrul mai afișează durata, codul din
    catalog și planul lunar”). Codul se verifică pe catalog (refuz numit dacă nu există); durata din afara plajei lui -> avertisment."""
    from core import mf_registru as _mfr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    cod = str((corp or {}).get("cod_catalog") or "").strip().rstrip(".")
    if not cod:
        raise _erori.DateInvalide({"cod": "COD_CATALOG_LIPSA", "mesaj": "Scrie codul de clasificare din catalog (HG 2139/2004).",
                                   "camp": "mf-catalog-%d" % int(mijloc_id)})
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = repo_mijloace_fixe.seteaza_cod_catalog(cur, mijloc_id, cod)
            if not r:
                raise _erori.Inexistent("Mijlocul fix ales nu există în registrul firmei.")
            refuz, avert = _mfr.verifica_cod(cod, r[1])
            if refuz:
                conn.rollback()
                raise _erori.DateInvalide({"cod": "COD_CATALOG_NECUNOSCUT", "mesaj": refuz, "camp": "mf-catalog-%d" % int(mijloc_id)})
        conn.commit()
    if avert:   # afirmație tipată (P8): durata din afara plajei catalogului
        avert = dict(_af.afirmatie("neconformitate", "durata_catalog", avert, unde="mijlocul fix %s" % mijloc_id,
                                   regula="durata normală în plaja codului din Catalogul HG 2139/2004"), mesaj=avert)
    return {"id": mijloc_id, "cod_catalog": cod, "catalog": _mfr.catalog().get(cod), "afirmatii": [avert] if avert else []}


def _casare(conn, schema, mijloc_fix_id, data):
    """[lotul 13, deficiențele 518 / 519 / 522, comanda Costin 13.1] Casarea mijlocului fix ales din registru.

    518, verbatim: „nota debitează 2813 cu 4.200 deși contul are 2.600; 2813 ajunge cu sold invers 1.600, iar amortizarea lunilor lipsă
    (1.600) nu trece prin 6811 — profit mai mare cu 1.600. Nu refuză ca reevaluarea, nu cere data casării, nu arată nota, justificativul e
    «Listă de inventariere» în loc de proces-verbal de casare, activul devine «casat» înainte de validarea notei.”
    Acum: (1) amortizarea lunilor de dinaintea casării trebuie să fie ÎNREGISTRATĂ pe activ (rândurile lui, `mf_registru.inregistrat_pe_activ`
    — nu soldul contului, 522); lipsa lor se refuză, cu lunile și suma, ca la reevaluare (R192): ele se generează din registru (517), prin
    6811; (2) luna casării, care nu se poate înregistra înainte de sfârșitul ei, intră în nota casării: 6811 = 28xx (motorul de amortizare,
    `d406_active.amortizat_la_data`, socotește luna ieșirii — INTERPRETARE: OMFP 1802/2014 pct.238 alin.(2) amortizează „până la recuperarea
    integrală a valorii”, iar pct.243 alin.(1) trece valoarea neamortizată pe cheltuieli la scoaterea din evidență; alternativa respinsă,
    fără luna ieșirii, ar schimba motorul folosit și de reevaluare și de D406); (3) 28xx = 21x cu toată amortizarea, 6583 = 21x restul
    neamortizat; (4) documentul: procesul-verbal de casare; (5) activul se scoate din registru la VALIDAREA notei (`mf_note`, iesire)."""
    from datetime import date as _date, timedelta as _td
    from core import d406_active as _d406, inventariere as _iv, mf_note as _mfn, mf_registru as _mfr, amortizare_lunii as _amc
    mf_id = int(mijloc_fix_id)
    ref = _date.fromisoformat(str(data)[:10])
    with conn.cursor() as cur:
        mf = repo_mijloace_fixe.pentru_inventariere(cur, schema, mf_id)
        if not mf:
            # [R147] „inexistent/inactiv" lăsa omul să ghicească pe care din două.
            raise _erori.Inexistent("Mijlocul fix ales nu există în registrul firmei sau a fost casat. Alege-l din listă.")
        p = _mfn.iesire_in_asteptare(cur, schema, mf_id)
        if p:
            from core import eticheta_nota as _et
            raise _erori.DateInvalide("Casarea acestui mijloc fix e deja în ciorna %s: valideaz-o din Registrul jurnal sau șterge-o, nu o "
                                      "genera a doua oară." % _et.nota(cur, schema, p[0]))
        repo_contabilitate.search_path_firma(cur, schema)
        rows = repo_mijloace_fixe.toate(cur)
    den, ci, ca, val, rez, dnf, pif, met, reev, dcd, prel, dprel = mf
    mf_d = {"cod": den, "denumire": den, "cont_imobilizare": ci, "cont_amortizare": ca, "valoare": val, "rezidual": rez, "dnf_luni": dnf,
            "data_pif": pif, "metoda": met, "reevaluari": reev, "destinatie_cd": dcd, "amortizare_preluata": prel, "data_preluare": dprel}
    if pif and ref < pif:
        raise _erori.DateInvalide({"mesaj": "Data casării (%s) e înaintea punerii în funcțiune a activului (%s)." % (data_ro(ref), data_ro(pif)),
                                   "erori_campuri": [{"camp": "op-data", "mesaj": "Data casării e înaintea punerii în funcțiune."}]})
    luna_dinainte = ref.replace(day=1) - _td(days=1)
    am_total = Decimal(str(_d406.amortizat_la_data(mf_d, ref)["amortizat"]))
    am_inainte = Decimal(str(_d406.amortizat_la_data(mf_d, luna_dinainte)["amortizat"])) if not pif or luna_dinainte >= pif else Decimal("0")
    with conn.cursor() as cur:
        repo_contabilitate.search_path_firma(cur, schema)
        inreg = _mfr.inregistrat_pe_activ(cur, schema, rows, mf_id, luna_dinainte)
        luna_inreg = (ref.year, ref.month) in _mfn.pe_activ(cur, schema, ref).get(mf_id, {}).get("luni", set())
        reg = next((x for x in _mfr.registru(cur, rows) if x["id"] == mf_id), {})
    if inreg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) < am_inainte.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP):
        lipsa = am_inainte - inreg
        luni = reg.get("luni_neinregistrate") or []
        raise _erori.DateInvalide(
            "Casarea lui %s nu se poate genera: până la %s amortizarea calculată e %s, dar pe activ sunt înregistrați %s — lipsesc %s%s. "
            "Fără ele, nota ar scădea din %s o amortizare pe care evidența n-o are (sold invers), iar lunile lipsă n-ar trece prin 6811 "
            "(profit mai mare cu suma lor). Înregistrează întâi lunile lipsă (registrul mijloacelor fixe, „Înregistrează lunile lipsă”), "
            "valideaz-le, apoi casează." % (den, data_ro(luna_dinainte), bani(am_inainte, "lei"), bani(inreg, "lei"), bani(lipsa, "lei"),
                                            (" (lunile %s)" % luni_ca_text(luni)) if luni else "", ca))
    rata_luna = Decimal("0") if luna_inreg else am_total - am_inainte
    ci, ca = _amc.conturile_fisei(den, ci, ca, (inreg + rata_luna) > 0)   # [C129, clasa] casarea, ca reevaluarea
    r = _iv.nota_casare_mf(val, inreg + rata_luna, ci, ca)
    if rata_luna > 0:   # luna casării: amortizarea ei, pe 6811, în nota casării
        r["linii"].insert(0, (_amc.CONT_CHELTUIALA, ca, rata_luna))
    r["d0"] = f"Casare {den} (PV comisie, neamortizat {bani(r['neamortizat'], 'lei')})"   # [lotul 10, 430e, clasa]
    r["mijloc_fix_id"] = mf_id
    return r


def luni_ca_text(luni):
    """[„05/2026”, „06/2026”] -> „05–06/2026” (lunile consecutive se strâng, ca în registru)."""
    from core import mf_registru as _mfr
    return _mfr.luni_ca_interval(sorted((int(x.split("/")[1]), int(x.split("/")[0])) for x in luni))


def _numar_inventar(cur, schema, dat):
    """[lotul 13, deficiența 521] „activul primește codul «MF-PLUS» în loc de număr de inventar”: numărul scris de contabil sau, fără
    el, următorul număr din șirul registrului (MF-001, MF-002 …)."""
    dat = str(dat or "").strip()
    if dat:
        return dat
    import re as _re
    nr = [int(m.group(1)) for c in repo_mijloace_fixe.coduri(cur, schema) for m in [_re.fullmatch(r"MF-(\d+)", str(c or ""))] if m]
    return "MF-%03d" % ((max(nr) if nr else 0) + 1)


def cont_amortizare_pentru(cont_imobilizare):
    """Contul de amortizare al contului de imobilizare (OMFP 1802/2014, planul de conturi: 2131 -> 2813, 205 -> 2805, 214 -> 2814 —
    „28” + grupa imobilizării). Nu se mai cere de mână (deficiențele 511 / 504)."""
    c = str(cont_imobilizare or "").strip()
    return ("28" + c[1:3]) if len(c) >= 3 and c[0] == "2" and c[1] in "01" else None


def _verifica_catalog(cod, dnf_luni, camp_cod="op-cod_catalog", camp_durata="op-dnf_luni"):
    """[lotul 13, deficiența 521] Codul din Catalogul HG 2139/2004 e cerut, iar durata se alege în plaja lui — HG 2139/2004, anexa, cap.I
    pct.4: „pentru fiecare mijloc fix nou achiziționat se utilizează sistemul unor plaje de ani cuprinse între o valoare minima și una
    maxima, existând astfel posibilitatea alegerii duratei normale de funcționare cuprinsa între aceste limite.”"""
    from core import mf_registru as _mfr
    c = _mfr.catalog().get(str(cod or "").strip().rstrip("."))
    if not c:
        m = ("Scrie codul de clasificare din Catalogul HG 2139/2004 (de exemplu 2.2.9 pentru calculatoare): durata normală de funcționare "
             "se alege în plaja lui.") if not str(cod or "").strip() else ("Codul %s nu e în Catalogul HG 2139/2004." % cod)
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp_cod, "mesaj": m}]})
    try:
        d = int(dnf_luni)
    except (TypeError, ValueError):
        d = 0
    if not (c["ani_min"] * 12 <= d <= c["ani_max"] * 12):
        m = ("Durata trebuie aleasă în plaja catalogului pentru codul %s (%s): între %d și %s (%d–%s)."
             % (cod, c["denumire"], c["ani_min"] * 12, _common.cate(c["ani_max"] * 12, "lună", "luni"), c["ani_min"],
                _common.cate(c["ani_max"], "an", "ani")))
        raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp_durata, "mesaj": m}]})
    return c


def nota_inventariere(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-inventariere`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import inventariere as _iv, mf_note as _mfn
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        mf_id = None
        tip_doc = "lista_inventariere"
        try:
            _uc_comun._campuri_lipsa(corp, {"plus": ("valoare",), "plus_mf": ("valoare", "denumire", "cont_imobilizare", "cod_catalog",
                                                                               "dnf_luni", "data_pif", "metoda"),
                                            "minus": ("valoare", "cota"), "casare": ("data", "mijloc_fix_id")
                                            }.get(op, ()))   # [lotul 11, 440 / A4] toate câmpurile lipsă deodată
            if op == "plus":
                r = _iv.nota_plus(corp["valoare"], _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc"))
                d0 = "Plus la inventar stocuri"
            elif op == "plus_mf":
                # [ruptura mijloc-fix post-migrare 14.08.2026] valideaza (art.28 alin.5/8^1) SI inscrie activul in registru.
                # [lotul 13, 521] codul din catalog cerut, durata în plaja lui, contul de amortizare din contul activului, numărul de
                # inventar al șirului registrului; [519] activul intră în registru la VALIDAREA notei (`mf_note`, intrare)
                ci = _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare")
                _verifica_catalog(corp.get("cod_catalog"), corp.get("dnf_luni"))
                mf_reg = _iv.pregateste_mf_plus(dict(corp, cont_imobilizare=ci, cont_amortizare=cont_amortizare_pentru(ci),
                                                     destinatie_cd=_uc_comun.bifa(corp, "destinatie_cd", False)))
                r = _iv.nota_plus_mf(corp["valoare"], mf_reg["cont_imobilizare"])
                d0 = "Plus la inventar mijloace fixe (21x=4754)"
            elif op == "minus":
                # [lotul 13, deficiența 520] întrebarea e criteriul legal (CF art.304 alin.(2) lit.a)): lipsa e DOVEDITĂ ca distrugere, pierdere
                # sau furt, cu documentul aferent — nu „era asigurat”; documentul se cere și intră în explicația notei. Imputarea către
                # salariat îl alege din salariații firmei (rândul 4282 îl poartă, ca reținerea să ajungă în stat — 506).
                dovedita = _uc_comun.bifa(corp, "lipsa_dovedita")
                if dovedita and not str(corp.get("document_lipsa") or "").strip():
                    raise _erori.DateInvalide({"mesaj": "Scrie documentul care dovedește distrugerea, pierderea sau furtul (de exemplu procesul-verbal "
                                                        "al organelor judiciare): fără el TVA dedusă se ajustează (CF art.304 alin.(2) lit.a)).",
                                               "erori_campuri": [{"camp": "op-document_lipsa", "mesaj": "Scrie documentul doveditor."}]})
                imputabil = _uc_comun.bifa(corp, "imputabil", False)
                sal = None
                if imputabil and corp.get("vinovat", "salariat") == "salariat":
                    with conn.cursor() as cur:
                        sal = _salariat_decont(cur, schema, corp.get("salariat_id"), _date.fromisoformat(str(corp["data"])[:10]))
                r = _iv.nota_minus(corp["valoare"], _cv.cere_cont(conn, schema, corp.get("cont_stoc"), "cont_stoc"),
                                   imputabil,
                                   corp.get("valoare_imputare"),
                                   corp.get("vinovat", "salariat"),
                                   _common.cota_ceruta(corp),
                                   dovedita)
                r["salariat"] = sal
                if dovedita:
                    r["document_lipsa"] = str(corp["document_lipsa"]).strip()
                d0 = "Minus la inventar" + (" imputabil" + (" — " + sal["nume"] if sal else "") if imputabil else " neimputabil") + \
                    ((" (lipsă dovedită: %s)" % r["document_lipsa"]) if dovedita else "")
            elif op == "casare":
                r = _casare(conn, schema, corp["mijloc_fix_id"], corp["data"])
                mf_id, d0, tip_doc = r["mijloc_fix_id"], r["d0"], "pv_casare"
            else:
                raise ValueError(nomenclator_cerut("operatie", "plus|plus_mf|minus|casare"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 2861/2009"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200], tip_doc)[0]
            mf_nou_id = None
            if op == "plus_mf":
                # [lotul 10, C73] cursa dintre două salvări cu același număr -> refuz numit
                _cod_mf = _numar_inventar(cur, schema, corp.get("numar_inventar"))
                try:
                    mf_nou_id = repo_mijloace_fixe.adauga_cu_reevaluare(cur, schema, _cod_mf, mf_reg["denumire"], mf_reg["cont_imobilizare"], mf_reg["cont_amortizare"], mf_reg["valoare"], mf_reg["rezidual"], mf_reg["dnf_luni"], mf_reg["data_pif"], mf_reg["metoda"], mf_reg["destinatie_cd"])[0]
                except _chei.CheieDublata as e:
                    raise _erori.DateInvalide(e.detaliu())
                repo_mijloace_fixe.seteaza_cod_catalog_schema(cur, schema, mf_nou_id, str(corp["cod_catalog"]).strip().rstrip("."))
                repo_mijloace_fixe.in_asteptarea_validarii(cur, schema, mf_nou_id)   # [519] până la validare
                _mfn.leaga(cur, schema, mf_nou_id, iid, "intrare")
                mf_id = mf_nou_id
            elif op == "casare":
                _mfn.leaga(cur, schema, mf_id, iid, "iesire")   # [519] activul iese din registru la VALIDAREA notei
            for dd, cc, ss in r["linii"]:
                if mf_id and (dd.startswith("2") or cc.startswith("2") or dd.startswith("68")):   # [522] rândurile activului
                    _mfn.adauga_linie(cur, schema, iid, dd, cc, ss, mf_id)
                elif r.get("salariat") and dd == "4282":   # [520 / 506] imputarea, pe salariat
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, r["salariat"]["cif"], r["salariat"]["nume"])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    rez_out = {"inregistrare_id": iid, "linii": [[a, b, str(c)] for a, b, c in r["linii"]]}
    if mf_nou_id:
        rez_out["mijloc_fix_id"] = mf_nou_id
        rez_out["numar_inventar"] = _cod_mf
    return _uc_comun.cu_eticheta(schema, rez_out)


def _partaj_lichidare(conn, schema, data):
    """[lotul 13, deficiența 533, comanda Costin 13.1] „capital, rezerve și profit scrise de mână (511), fără verificarea soldurilor (524) și
    fără împărțire pe asociați”; „nota debitează 1171 deși profitul F2 stă pe 117 (527)”. Acum: capitalul (1012), rezervele (106x) și
    profitul (117x, 121) vin din SOLDURILE lor la data partajului (soldurile preluate + notele validate, `bilant_api.sold_la`), din contul
    care le are; se împart pe asociații de la data partajului (Date firmă → Asociați, cotele), fiecare cu rândurile lui (456 pe
    asociat): capitalul neimpozabil, câștigul (rezerve + profit) impozitat cu cota CF art.97 alin.(5) — verbatim: „Venitul impozabil
    obținut din lichidarea unei persoane juridice de către acționari/asociați persoane fizice […] se impun cu o cotă de 10%, impozitul
    fiind final” (forma consolidată; Legea 141/2025 art.II pct.5 a modificat numai alin.(7), dividendele, la 16%). -> (rezultat, info)."""
    from decimal import Decimal as _D
    from psycopg2.extras import RealDictCursor
    from core import bilant_api as _ba, lichidare as _li, dividende_curs as _dc, repo_d205 as _rd, decontari_asociati as _da
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        sold = _ba.sold_la(cur, schema, data)
        repo_contabilitate.search_path_firma(cur, schema)
        asoc, istoric = _rd.select_asociati(cur), _rd.select_asociati_istoric(cur)
    if sold is None:
        raise _erori.DateInvalide("Data partajului e înaintea soldurilor preluate: capitalul, rezervele și profitul nu se cunosc la ea.")
    cred = {k: c - d for k, (d, c) in sold.items() if c - d > 0}
    capital = {k: v for k, v in cred.items() if str(k).startswith("1012")}
    rezerve = {k: v for k, v in cred.items() if str(k).startswith("106")}
    profit = {k: v for k, v in cred.items() if str(k).startswith("117") or str(k).startswith("121")}
    if not (capital or rezerve or profit):
        raise _erori.DateInvalide("La %s nu e nimic de împărțit: capitalul (1012), rezervele (106x) și profitul (117x, 121) n-au sold creditor "
                                  "(din soldurile preluate și notele validate)." % data_ro(data))
    structura = _dc.structura_la([(a["nume"], a.get("cnp"), a["cota"]) for a in asoc],
                                 [(r["cnp"], r["nume"], r["cota"], r["valabil_pana_la"]) for r in istoric])(data)
    if not structura:
        raise _erori.DateInvalide(_uc_comun.refuz_spre_ecran(_da.FARA_ASOCIATI, None, "date_firma", "Legea 31/1990 art.67 alin.(2)",
                                                             tip="partajul lichidării"))
    cota_impozit = _li._cota_lichidare(data)
    linii, pe_asociat = [], []
    tot = {"capital": _D("0"), "castig": _D("0"), "impozit": _D("0"), "net": _D("0")}
    def impartire(v):   # partea fiecărui asociat, rotunjită la ban; restul rotunjirii la ultimul (suma părților = soldul)
        p = [(v * _D(str(a[2])) / 100).quantize(_D("0.01"), rounding=ROUND_HALF_UP) for a in structura]
        p[-1] = v - sum(p[:-1], _D("0"))
        return p
    conturi = list(capital.items()) + list(rezerve.items()) + list(profit.items())
    parti = {k: impartire(v) for k, v in conturi}
    for i, a in enumerate(structura):
        cnp, nume, c = a[0], a[1], _D(str(a[2]))   # `structura_la` dă (cnp, nume, cota)
        cif = _cif_partener(cnp)
        cap_i = sum((parti[k][i] for k in capital), _D("0"))
        castig_i = _D("0")
        for k, _v in conturi:
            p_ = parti[k][i]
            if p_ > 0:
                linii.append((str(k), "456", p_, cif, nume))
                if not str(k).startswith("1012"):
                    castig_i += p_
        imp_i = (castig_i * cota_impozit / 100).quantize(_D("0.01"), rounding=ROUND_HALF_UP)
        if imp_i > 0:
            linii.append(("456", "446", imp_i, cif, nume))
        net_i = cap_i + castig_i - imp_i
        linii.append(("456", "5121", net_i, cif, nume))
        pe_asociat.append({"nume": nume, "cota": str(c), "capital": str(cap_i), "castig": str(castig_i), "impozit": str(imp_i), "net": str(net_i)})
        for k2, v2 in (("capital", cap_i), ("castig", castig_i), ("impozit", imp_i), ("net", net_i)):
            tot[k2] += v2
    info = {"castig_impozabil": str(tot["castig"]), "impozit": str(tot["impozit"]), "net_asociat": str(tot["net"]), "cota": str(cota_impozit),
            "asociati": pe_asociat, "solduri": {k: str(v) for k, v in {**capital, **rezerve, **profit}.items()}}
    return {"linii": linii}, info


def nota_lichidare(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-lichidare`; docstringul ei a ramas in stratul HTTP."""
    from datetime import date as _date
    from core import lichidare as _li
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie")
        info = {}
        try:
            _uc_comun._campuri_lipsa(corp, {"vanzare_activ": ("pret", "valoare_bruta", "amortizare_cumulata", "cota"),
                                            "partaj": ("data",)}.get(op, ()))   # [lotul 11, 440 / A4]
            if op == "vanzare_activ":
                r = _li.nota_vanzare_activ(corp["pret"], corp["valoare_bruta"],
                                           corp["amortizare_cumulata"],
                                           _cv.cere_cont(conn, schema, corp.get("cont_imobilizare"), "cont_imobilizare", "2131"),
                                           _cv.cere_cont(conn, schema, corp.get("cont_amortizare"), "cont_amortizare", "2813"),
                                           _common.cota_ceruta(corp))
                d0 = "Lichidare: valorificare activ (7583 + descarcare)"
            elif op == "partaj":
                r, info = _partaj_lichidare(conn, schema, _date.fromisoformat(corp["data"]))
                d0 = "Partaj lichidare pe asociați: capital neimpozabil + câștig impozitat (CF art.97 alin.(5))"
            else:
                raise ValueError(nomenclator_cerut("operatie", "vanzare_activ|partaj"))
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or d0) + " - OMFP 897/2015"
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for rand in r["linii"]:
                dd, cc, ss = rand[:3]
                if len(rand) > 3:   # [533] rândul asociatului, cu partenerul lui
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, rand[3], rand[4])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid,
            "linii": [[x[0], x[1], str(x[2])] for x in r["linii"]], **info})


def nota_ong(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/nota-ong`; docstringul ei a ramas in stratul HTTP."""
    from core import ong as _on
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        op = corp.get("operatie", "venit")
        try:
            _uc_comun._campuri_lipsa(corp, ("venituri_economice", "venituri_neimpozabile", "curs_eur") if op == "scutire" else ("suma",))   # [440 / A4]
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
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            for dd, cc, ss in r["linii"]:
                repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "cont_venit": r["cont_venit"],
            "linii": [[a, b, str(c)] for a, b, c in r["linii"]]})


def tenant_activare(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/activare`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        if not _uc_comun._acces_pentru_activare(conn, ctx["rol"], ctx.get("firm"), tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            _ex = repo_utilizatori.contul_dupa_email(cur, email)
            _uc_comun._refuza_email_ocupat(_ex, "client", email, "clientul firmei", "email")
            # [R62 (2)] Aceeasi ramura de reactivare exista si aici. Gardul repara CLASA, nu
            # instanta: daca ar sta doar pe ruta clientului, calea prin cabinet ar ramane deschisa.
            _uc_comun._cere_acelasi_cabinet(_ex, ctx["firm"])
            if _ex:  # client_mesaj_v1: reinvitare client dezactivat
                uid = _ex["id"]
                repo_utilizatori.activeaza_contul_cu_nume(cur, date.nume or email.split("@")[0], uid)
                repo_utilizatori.leaga_contul_de_firma_idempotent(cur, uid, tenant_id)
            el_creaza = _ex is None
            if el_creaza:
                # [lotul 10, C73 / U3] adresa luată între verificare și scriere -> același refuz ca verificarea, nu 500
                with _chei.refuza_dublura(cur, _uc_comun.CHEIE_EMAIL, _uc_comun._refuz_email_la_cursa("client", email, "clientul firmei",
                                                                                                    "email")):
                    uid = repo_utilizatori.creeaza_cont(cur, email, _nucleu.hash_parola(parola_temp), date.nume or email.split("@")[0],
                                                        ctx["firm"])["id"]
                repo_utilizatori.leaga_contul_de_firma(cur, uid, tenant_id)
            _uc_comun._urma_portal(cur, tenant_id, "acces_dat",
                         "cabinetul a dat acces la portal lui %s" % email,
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
    # [C39] mesajul cabinetului și numele firmei sunt scrise de om: escapate (rândurile noi ale mesajului rămân rânduri)
    _pm_html = ("<p style='border-left:3px solid #3d8fd6;padding-left:12px;color:#334155'>%s</p>"
           % _common.esc(date.mesaj.strip()).replace("\n", "<br>")) if (date.mesaj or "").strip() else ""  # client_mesaj_v1
    html = ("<p>Bună,</p>" + _pm_html + "<p>Ai primit acces la portalul iConta.eu pentru firma <b>%s</b>.</p>"
            "<p><a href='%s' style='display:inline-block;background:#3d8fd6;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none'>Intră în portal</a></p>"
            "<p>Linkul e valabil 48 de ore.</p>") % (_common.esc(d.get("nume", "")), link)
    # [R73] ALERTA: linkul e singura usa a clientului in portal (ca linkul de logare)
    # [lotul 13, 560 / 268] invitația e tranzacțională: pe Postmark (fără „Dezabonează-te”), Brevo rămâne rezervă (`observare`)
    _obs.trimite_email_html_sau_semnaleaza("email acces portal", email, "Acces portal iConta.eu — " + d.get("nume", ""), html,
                                           alerta=True, postmark=True)
    return {"ok": True, "user_id": uid}



def parteneri_incarca(tenant_id, continut, nume_fisier, ctx, cont_implicit=None):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/parteneri/incarca`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    ignorate = []   # [comanda Costin 8.2 pct.4] rândurile de total / titlu și partenerii cu sold 0: spuse, nu sărite în tăcere
    try:
        randuri = solduri_parteneri_api.extrage(continut, nume_fisier or "", cont_implicit=cont_implicit, ignorate=ignorate)
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    # [lotul 6] Un `.txt` cu o linie de proza intorcea `{"randuri": []}` — „fisierul n-are parteneri"
    # arata identic cu „fisierul n-a fost citit". A treia cale cu aceeasi gaura in lotul asta.
    if not randuri:
        raise _erori.DateInvalide("Din fișierul %s nu s-a putut citi niciun partener. Se așteaptă un "
                                 "CSV sau un XLSX cu solduri pe parteneri — un fișier necitit nu e "
                                 "un fișier gol." % (nume_fisier or "trimis",))
    td = round(sum(r["debit"] for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tc = round(sum(r["credit"] for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    er, bune = solduri_parteneri_api.verifica_randuri(randuri)
    with db.get_conn(schema) as conn:
        coer = solduri_parteneri_api.coerenta(conn, schema, bune)
        existent = solduri_parteneri_api.existent(conn)   # [426, clasa] soldurile pe parteneri deja salvate
        refuz_tvai = solduri_parteneri_api.refuz_tva_incasare(conn, schema, bune)   # [252, 12.3 pct.5] același refuz ca la salvare
    # [Q5] poarta unica; [346] + rândurile contului ale cărui solduri pe parteneri nu dau soldul lui la data preluării (pe ce ar intra)
    erori = migrare_api.erori_verifica((er, bune)) + solduri_parteneri_api.respinse_coerenta(bune, coer)
    # [426, clasa] „înainte de înlocuire: spune că există deja […], arată totalurile vechi și noi, cere confirmare” — pe rândurile care intră
    _nou = solduri_parteneri_api.totaluri(migrare_api.randuri_care_intra(randuri, erori))
    return _uc_comun._raspuns({"randuri": randuri, "total_debit": td, "total_credit": tc, "coerenta": coer, "erori": erori,
                               "ignorate": ignorate, "existenta": existent if existent["randuri"] else None,
                               "avertisment_inlocuire": solduri_parteneri_api.text_inlocuire(existent, _nou) if existent["randuri"] else None,
                               "refuz_tva_incasare": refuz_tvai,
                               **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]



def salariati_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salariati-import/incarca`; docstringul ei a ramas in stratul HTTP."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    continut = continut
    try:
        randuri = salariati_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    # [lotul 11, 420] pe salariații existenți, câmpul lipsă din fișier arată valoarea din fișă (pe care o păstrează salvarea), marcată
    with db.get_conn(schema) as conn:
        salariati_import_api.din_fise(conn, randuri)
    valizi = sum(1 for r in randuri if salariati_import_api.valideaza_cnp(r.get("cnp"))[0])   # [14.10] recalculat, ca la salvare
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
    salariati_import_api.eticheteaza(randuri)   # [comanda Costin 8.2 pct.4] starea fiecărui rând: ok / semnalat / respins, cu motivul
    # [426, clasa] salariații din fișier care există deja (același CNP): fișele lor se actualizează — spus înainte, cu confirmare
    _intra = migrare_api.randuri_care_intra(randuri, erori)
    with db.get_conn(schema) as conn:
        existent = salariati_import_api.existent(conn, [r.get("cnp") for r in _intra])
    return _uc_comun._raspuns({"randuri": randuri, "total": len(randuri), "valizi": valizi,
            "invalizi": len(randuri) - valizi, "erori": erori, "existenta": existent if existent["randuri"] else None,
            "avertisment_inlocuire": salariati_import_api.text_inlocuire(existent, {"randuri": len(_intra)}) if existent["randuri"] else None,
            **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]



def retete_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/randuri-import/incarca` — previzualizarea, pe rândurile fișierului [375]."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        randuri = retete_import_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    if not randuri:
        raise _erori.CerereGresita("fișierul nu conține niciun rând de rețetă")
    with db.get_conn(schema) as conn:
        retete_import_api.potriveste(conn, schema, randuri)
    # [375, comanda Costin 8.2 pct.4] fiecare rând citit, cu starea lui; rețetele se formează numai din rândurile care intră
    retete_import_api.eticheteaza(randuri)
    return _uc_comun._raspuns({"randuri": randuri, "rezumat": retete_import_api.rezumat(randuri),
                               "erori": retete_import_api.verifica_randuri(randuri), **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]



def rip_import_incarca(tenant_id, continut, nume_fisier, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/rip-import/incarca` — PREVIZUALIZAREA (nu scrie nimic).
    [372, comanda Costin 8.2] până azi ruta scria direct rândurile bune, fără previzualizare; acum fiecare rând citit se întoarce cu
    starea și motivul lui, iar salvarea e `rip_import_salveaza`."""
    _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        randuri = rip_migrare_api.extrage(continut, nume_fisier or "")
    except ValueError as e:
        raise _erori.CerereGresita(str(e))
    if not randuri:
        raise _erori.CerereGresita("fișierul nu conține operațiuni de import")
    rip_migrare_api.eticheteaza(randuri)
    erori = rip_migrare_api.verifica_randuri(randuri)   # [Q5] poarta unica previzualizare <-> salvare
    return _uc_comun._raspuns({"randuri": randuri, "total": len(randuri), "erori": erori, **_firma_fisier(tenant_id, continut, nume_fisier)})   # [599]


def rip_import_salveaza(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `POST /tenants/{tenant_id}/rip-import`: rândurile bune se scriu, cele respinse se spun numite."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    randuri = [r.model_dump() for r in date.randuri]
    with db.get_conn(schema) as conn:
        try:
            rez = rip_migrare_api.importa(conn, schema, randuri)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    respinse = rez["respinse"]
    # marcheaza stratul rip (public.migrare_status, per cabinet) pentru reminder()
    with db.get_conn() as conn:
        if respinse:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "in_lucru",
                                       f"{_common.cate(len({e['rand'] for e in respinse}), 'rând respins', 'rânduri respinse')} la import — de completat")
        else:
            migrare_api.seteaza_status(conn, ctx["firm"], "rip", "gata", "")
    return _uc_comun._raspuns(rez)



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



def facturi_previzualizare_lei(tenant_id, corp, ctx):
    """[lotul 10, comanda 10.2 pct.7g] „Factură în valută: cursul BNR și TVA-ul în lei nu se văd înainte de emitere.” Corpul rutei
    `/tenants/{tenant_id}/facturi/previzualizare-lei`: cursul cu care va emite `facturi/emite` (aceeași descărcare BNR înaintea tranzacției,
    același `facturi_api.curs_automat`) și TVA-ul / totalul în lei ale liniilor date — nimic scris."""
    import datetime as _dt
    from decimal import Decimal as _D, InvalidOperation as _IO
    corp = corp or {}
    moneda = str(corp.get("moneda") or "").strip().upper()
    if not moneda:
        raise _erori.CerereGresita("Moneda facturii lipsește.")
    try:
        data = _dt.date.fromisoformat(str(corp.get("data_emitere") or "")[:10])
    except ValueError:
        raise _erori.CerereGresita("Data emiterii lipsește sau nu e o dată din calendar.")
    # `linii` lipsă (null) = cota încă nestabilită pe o linie: numai cursul; o listă (și goală) = sumele în lei ale ei
    linii = None if corp.get("linii") is None else []
    for i, l in enumerate(corp.get("linii") or [], 1):
        try:
            v = {k: _D(str(l[k])) for k in ("cantitate", "pret_unitar", "cota_tva")}
        except (KeyError, TypeError, _IO):
            v = None
        if v is None or not all(x.is_finite() for x in v.values()):
            raise _erori.CerereGresita("Linia %d: cantitatea, prețul și cota TVA trebuie să fie numere." % i)
        linii.append(v)
    _uc_comun._preincalzeste_cursul(moneda, data)   # [P5 val 3] descărcarea BNR, înainte de tranzacție — ca la emitere
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        out = facturi_api.previzualizare_lei(conn, moneda, data, linii)
    # [460] cursul zilei lipsă (ultimul comunicat înaintea datei facturii, HG 1/2016 pct.35 alin.(1)): ce lipsește și ce se folosește
    if out.get("ok") and out.get("data_curs"):
        from core import curs_bnr as _cb_p
        # [lotul 12, decizia „cursul vechi la validare (a)”] ecranul facturii primite cere anunțul cu actul ei (validarea)
        out["curs_zilei_lipsa"] = _cb_p.cursul_zilei_lipsa(data, _dt.date.fromisoformat(out["data_curs"]),
                                                       act="validare" if corp.get("act") == "validare" else "emitere")
    return out


def facturi_emite(tenant_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/emite`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._preincalzeste_cursul(date.moneda, date.data_emitere)   # [P5 val 3] descărcarea BNR, înainte de tranzacție
    _tert_pl = _uc_comun._platitor_tva_tert(date.tert_cui, date.tert_tara)   # [pct.5] „RO” pe factură, tot înainte de tranzacție
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    linii = [l.model_dump() for l in date.linii]
    if not (date.tert_nume or "").strip():
        # [lotul 11, deficiența 440] denumirea lipsă și liniile incomplete (`facturi_api.linii_campuri_lipsa`, aceeași validare ca la
        # emitere) se spun DEODATĂ, fiecare lângă câmpul ei din Emitere (`em-nume`, `em-l{i}-…`); înainte, denumirea oprea tot
        er = _erori.ErorileFormularului("Factura nu s-a emis")
        er.camp("em-nume", "Denumirea beneficiarului e obligatorie pe factură. Completeaz-o înainte de emitere.")
        for x in (facturi_api.linii_campuri_lipsa(linii) if linii else []):
            er.camp(x["camp"], x.get("mesaj") or x["eticheta"])
        er.refuza()
    _ai = _uc_comun._intreaba_modelul(schema, linii)   # [R193] modelul, înaintea tranzacției de emitere
    # [lotul 13, C199] livrarea intracomunitară: codul de TVA al clientului în VIES, pe server, înaintea tranzacției (ca `vanzare_ic`, P5);
    # invalid -> refuzul scutirii, indisponibil -> avertisment (550) — `facturi_api.emite_factura`
    _vies = facturi_api.verifica_vies_emitere(date.tert_cui, date.tert_tara) if facturi_api.cere_vies(date.tip, linii) else None
    with db.get_conn(schema) as conn:
        din_bon = bool((date.bon_fiscal_nr or "").strip())
        if din_bon and date.pleaca_marfa is True:
            # [decizia A 02.10] marfa a plecat cu bonul fiscal (raportul Z): a doua descărcare ar scoate-o de două ori din stoc
            raise _erori.DateInvalide(MESAJ_FACTURA_BON_STOC)
        # poarta doar la FACTURA (nu proforma/aviz), cu linie de stoc; nu și la factura din bon (fără descărcare) — aceeași condiție
        # ca la transformarea proformei / avizului (C63)
        poarta_ceruta = facturi_api.poarta_marfa_ceruta(date.tip, linii, date.bon_fiscal_nr)
        # [lotul 13, regula UM — `facturi.um_lipsa`, decizia sesiunii principale 26.10.2026] UM-ul gol nu devine „buc”: se refuză lângă
        # câmpul liniei (al articolului din nomenclator se ia de la articol), împreună cu celelalte câmpuri lipsă ale liniilor (440)
        _um_lipsa = facturi_api.um_lipsa_emitere(conn, linii)
        # [lotul 13, 536] centrul de cost al liniei: un centru activ al firmei (sau niciunul), refuzat lângă câmpul liniei
        from core import centre_cost_api as _cc
        with conn.cursor() as _cur_cc:
            _um_lipsa += _cc.campuri_centru_gresit(_cur_cc, schema, [l.get("centru_cost_id") for l in linii], lambda i: "em-l%d-centru" % i)
        if _um_lipsa:
            er = _erori.ErorileFormularului("Factura nu s-a emis")
            for x in facturi_api.linii_campuri_lipsa(linii):
                er.camp(x["camp"], x.get("mesaj") or x["eticheta"])
            for camp, mesaj in _um_lipsa:
                er.camp(camp, mesaj)
            er.refuza()
        platitor = _uc_comun._platitor_tva_firma(conn)
        try:
            r = facturi_api.emite_factura(
                conn, linii, client_id=date.client_id, tert_nume=date.tert_nume,
                tert_cui=date.tert_cui, tert_adresa=date.tert_adresa, data_emitere=date.data_emitere,
                data_scadenta=date.data_scadenta, moneda=date.moneda,
                platitor_tva=platitor, curs_manual=date.curs_manual, tip=date.tip,
                tert_tara=date.tert_tara, tip_operatiune=date.tip_operatiune,
                data_curs_manual=date.data_curs_manual,
                bon_fiscal_nr=date.bon_fiscal_nr, bon_fiscal_data=date.bon_fiscal_data,
                tert_platitor_tva=_tert_pl, pleaca_marfa=date.pleaca_marfa,   # [06.10.2026 §6.3]
                intreaba_marfa=poarta_ceruta,   # [304] întrebarea, după verificarea liniilor (refuzul lor vine întâi)
                raspunsuri_ai=_ai, categorie_331=date.categorie_331,   # [274b] categoria produsului la taxarea inversă
                tert_oras=date.tert_oras, tert_judet=date.tert_judet,   # [274b] adresa clientului străin (livrarea intracomunitară)
                # [lotul 12, C84, decizia Costin 12.3 pct.7] livrarea intracomunitară de bunuri: întrebarea dovezii transportului (ca
                # „Pleacă marfa acum?”); „Nu” emite, cu avertisment. Câmpul `EmitereIn.dovada_transport` (main.py)
                intreaba_dovada=True, dovada_transport=getattr(date, "dovada_transport", None),
                vies=_vies,   # [lotul 13, C199] răspunsul VIES, cerut înaintea tranzacției
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
            if getattr(e, "cod", None) == facturi_api.COD_INTREABA_MARFA:
                raise _erori.DateInvalide({"ok": False, "cod": facturi_api.COD_INTREABA_MARFA, "mesaj": str(e)})
            if getattr(e, "cod", None) == facturi_api.COD_INTREABA_DOVADA:   # [lotul 12, C84] întrebarea, nu un refuz: nimic scris
                raise _erori.DateInvalide({"ok": False, "cod": e.cod, "mesaj": str(e), "intrebare": e.intrebare})
            if getattr(e, "cod", None) in ("METODA_STOC_NEDECLARATA", "METODA_STOC_ALTA"):
                # [06.10.2026 §6.3] refuz STRUCTURAT spre Date firmă (metoda de stoc), factura păstrată pe ecran
                from core import capital_social as _cs
                raise _erori.DateInvalide(_cs.detaliu_metoda_stoc(e))
            if getattr(e, "cod", None) == facturi_api.COD_SERIE_LIPSA:
                # [06.10.2026 §6.1] refuz STRUCTURAT: ecranul setează seria peste factură și emiterea continuă
                raise _erori.DateInvalide(facturi_api.detaliu_serie_lipsa(e))
            if getattr(e, "cod", None) == facturi_api.COD_VIES_INVALID:   # [lotul 13, C199] lângă codul clientului
                raise _erori.DateInvalide({"cod": e.cod, "mesaj": str(e), "erori_campuri": [{"camp": "em-cui", "mesaj": str(e)}]})
            if getattr(e, "cod", None) == "CAPITAL_SOCIAL_LIPSA":
                # [lot 19 d12] refuz STRUCTURAT: ecranul păstrează factura și oferă butonul spre Date firmă
                from core import capital_social as _cs
                raise _erori.DateInvalide(_cs.detaliu(e))
            raise _erori.DateInvalide(str(e))
        # [comanda Costin 05.10.2026 pct.3] cota schimbată față de propunere se consemnează (propus → ales, cine, când), în
        # ACEEAȘI tranzacție cu factura: o factură emisă fără rândul ei de jurnal nu poate exista
        if isinstance(r, dict) and r.get("factura_id"):
            with conn.cursor() as cur:
                repo_facturi.jurnalizeaza_cota_aleasa(cur, r["factura_id"], linii, ctx["uid"])
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



def linii_din_proforma(linii):
    """[C63, găsită de Code 19.10.2026] Liniile facturii născute dintr-o proformă / un aviz: ce a scris omul pe document trece pe
    factură — și unitatea de măsură și contul de venit (înainte: „buc” și contul ghicit din denumire). CF art.319 alin.(20) lit.h:
    factura cuprinde „denumirea și cantitatea bunurilor livrate, denumirea serviciilor prestate”. Și articolul de stoc trece (decizia
    Costin 19.10.2026, „Închiderea lotului 9”: „la transformarea în factură se pune aceeași întrebare ca la orice factură, «Pleacă
    marfa acum?»”): factura cu articol întreabă ca la emitere (`facturi_api.poarta_marfa_ceruta`), iar marfa se descarcă o singură dată,
    numai la „Da” (`proforma_transforma`)."""
    return [{"descriere": l.get("descriere"), "cantitate": l.get("cantitate"), "um": l.get("um") or "buc",
             "pret_unitar": l.get("pret_unitar"), "cota_tva": l.get("cota_tva"), "cont_venit": l.get("cont_venit"),
             "categorie_tva": l.get("categorie_tva"),   # [274b] categoria aleasă pe proformă trece pe factură
             "articol_id": l.get("articol_id"),   # [C63] articolul de stoc: întrebarea „Pleacă marfa acum?” și descărcarea la „Da”
             "centru_cost_id": l.get("centru_cost_id")}   # [lotul 13, 536] centrul de cost al liniei trece pe factură
            for l in linii]


def antet_din_proforma(f):
    """[C63] Beneficiarul și operațiunea facturii născute dintr-o proformă / un aviz: aceleași ca pe document. Înainte se pierdeau adresa
    (CF art.319 alin.(20) lit.f: „denumirea/numele și adresa beneficiarului”), localitatea / județul (eFactura regula BR-RO-110) și tipul
    operațiunii (o livrare intracomunitară ar fi ieșit „normală”)."""
    return {"client_id": f.get("client_id"), "tert_nume": f.get("tert_nume"), "tert_cui": f.get("tert_cui"),
            "tert_adresa": f.get("tert_adresa"), "tert_oras": f.get("tert_oras"), "tert_judet": f.get("tert_judet"),
            "moneda": f.get("moneda") or "RON", "tert_tara": f.get("tert_tara") or "RO",
            "tip_operatiune": f.get("tip_operatiune") or "normal", "tert_platitor_tva": f.get("tert_platitor_tva"),
            "categorie_331": f.get("categorie_331")}   # [274b] categoriile, verificate pe țara clientului


def proforma_transforma(tenant_id, factura_id, ctx, pleaca_marfa=None, dovada_transport=None):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi/{factura_id}/transforma`; docstringul ei a ramas in stratul HTTP.

    [C63, decizia Costin 19.10.2026] Factura născută din proformă / aviz cu articol de stoc întreabă „Pleacă marfa acum?” exact ca
    emiterea din formular: aceeași condiție (`facturi_api.poarta_marfa_ceruta`), același refuz structurat (`COD_INTREABA_MARFA`, nimic
    scris), aceeași descărcare la „Da” (`stocuri_cv_api.descarca_factura`, în tranzacția emiterii); la „Nu” stocul nu se atinge.

    [lotul 12, C84 / C157, deciziile Costin 12.3 pct.7 și pct.3] Aceeași regulă ca „Emite factură” (`facturi_emite`): livrarea
    intracomunitară de bunuri întreabă „Ai dovada transportului?” (`COD_INTREABA_DOVADA`, cu `intrebare`, nimic scris), iar „Nu” emite cu
    avertisment; avertismentele emiterii (`avertismente`: și neplătitorul neînregistrat art.317) vin în răspuns, ca la emitere."""
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    # [P5 val 3] Moneda se citeste intr-o tranzactie SCURTA, apoi cursul se aduce — amandoua
    # inaintea tranzactiei de emitere, ca descarcarea BNR sa nu tina o conexiune din pool.
    import datetime as _dtx
    _uc_comun._preincalzeste_cursul(_uc_comun._moneda_facturii(schema, factura_id), _dtx.date.today())

    def _linii_proformei(conn):
        return linii_din_proforma((facturi_api.detalii_factura(conn, factura_id) or {}).get("linii") or [])
    # [R193] liniile proformei se citesc într-o tranzacție scurtă, modelul se întreabă cu pool-ul liber, iar tranzacția de mai jos
    # le recitește: o linie schimbată între timp n-are răspuns, deci cota ei iese nedeterminată, nu ghicită
    with db.get_conn(schema) as conn:
        _linii0 = _linii_proformei(conn)
        _ant0 = antet_din_proforma(facturi_api.detalii_factura(conn, factura_id) or {})
    _ai = _uc_comun._intreaba_modelul(schema, _linii0)
    # [lotul 13, C199] ca la „Emite factură”: livrarea intracomunitară verifică în VIES codul clientului, înaintea tranzacției
    _vies = facturi_api.verifica_vies_emitere(_ant0.get("tert_cui"), _ant0.get("tert_tara")) if facturi_api.cere_vies("factura", _linii0) else None
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            r = repo_facturi.tip_si_transformare(cur, factura_id)
        if not r:
            raise _erori.Inexistent("document inexistent")
        if r[0] == "factura":
            raise _erori.DateInvalide("documentul e deja factura")
        from core import nomenclator_status_factura as _nsf
        if _nsf.e_sold_preluat(r[0]):   # [lotul 12, 252] factura deschisă preluată nu se transformă
            raise _erori.DateInvalide(_nsf.MESAJ_SOLD_PRELUAT)
        if r[1]:
            # [lotul 12, 443.1] factura numită ca în Istoric („Factură F1A nr. 12 din 05.10.2026”), nu prin id-ul ei intern
            from core import eticheta_nota as _et_tr
            with conn.cursor() as cur:
                raise _erori.Conflict("documentul a fost deja transformat: %s" % _et_tr.factura(cur, schema, r[1]))
        f = facturi_api.detalii_factura(conn, factura_id)
        linii = _linii_proformei(conn)
        poarta_ceruta = facturi_api.poarta_marfa_ceruta("factura", linii)   # [C63] ca la emitere; documentul nou nu vine din bon
        platitor = _uc_comun._platitor_tva_firma(conn)
        try:
            rez = facturi_api.emite_factura(conn, linii, platitor_tva=platitor, raspunsuri_ai=_ai,
                                            # [lotul 12, C84] întrebarea dovezii transportului, ca la „Emite factură” (`facturi_emite`)
                                            intreaba_dovada=True, dovada_transport=dovada_transport, vies=_vies,   # [lotul 13, C199]
                                            intreaba_marfa=poarta_ceruta, pleaca_marfa=pleaca_marfa, **antet_din_proforma(f))
        except ValueError as e:
            if getattr(e, "cod", None) == facturi_api.COD_INTREABA_MARFA:
                raise _erori.DateInvalide({"ok": False, "cod": facturi_api.COD_INTREABA_MARFA, "mesaj": str(e)})
            if getattr(e, "cod", None) == facturi_api.COD_INTREABA_DOVADA:   # [lotul 12, C84] întrebarea, nu un refuz: nimic scris
                raise _erori.DateInvalide({"ok": False, "cod": e.cod, "mesaj": str(e), "intrebare": e.intrebare})
            if getattr(e, "cod", None) in ("METODA_STOC_NEDECLARATA", "METODA_STOC_ALTA"):
                # [C63] refuzul metodei de stoc, structurat spre Date firmă — ca la emitere
                from core import capital_social as _cs
                raise _erori.DateInvalide(_cs.detaliu_metoda_stoc(e))
            raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            repo_facturi.leaga_proforma_de_factura(cur, rez["factura_id"], factura_id)
        if poarta_ceruta and pleaca_marfa is True:
            # [C63] descărcarea, o singură dată, în ACEEAȘI tranzacție cu factura (atomic: emitere + descărcare), ca la emitere
            from core import stocuri_cv_api as _cv
            rez["descarcare"] = _cv.descarca_factura(conn, schema, rez["factura_id"], _dtx.date.today().isoformat())
        conn.commit()
    return rez



def salarii_contare_scrie(tenant_id, an, luna, ctx, confirma=False):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/salarii-contare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    _uc_comun._cere_luna_incheiata(an, luna, "Salariile lunii")   # [deficiența 216]
    from core import salarii_contare as _sc
    schema = _uc_comun._schema_cabinet_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        # [R42 (a)] Nota poarta ultima zi a lunii declarate; intr-o luna inchisa nu se scrie.
        # [lotul 07.10 pct.7, decizia Costin 06.10.2026] Forma veche scria ziua 28 sub comentariul de mai sus: nicio normă nu
        # cere 28 (a venit cu afb592ac, R33, fără temei), deci data e ultima zi a lunii — cea pe care comentariul o promitea.
        ultima = _uc_comun.ultima_zi_a_lunii(an, luna)
        _uc_comun._cere_luna_deschisa(conn, schema, ultima)
        try:
            p = _sc.propunere(conn, schema, an, luna)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        with conn.cursor() as cur:
            r = repo_contabilitate.id_nota_dupa_numar_2(cur, p["document_ref"])
            inlocuita = ciorna_veche = None
            if r:
                # [lotul 07.10 B, C9, decizia Costin] „recontabilizarea înlocuiește nota respinsă și o retrimite la validare”:
                # nota respinsă (ciornă) se scoate și se scrie din statul corectat; noua ciornă intră singură în coadă
                # (`uc_coada.note_in_coada`). Nota validată rămâne — a doua notă n-ar avea temei.
                # [retest 08.10 pct.1, decizia Costin] „când statul se schimbă și există o ciornă nevalidată pentru aceeași lună,
                # contabilizarea o înlocuiește cu nota din statul de acum și o trimite la validare; nu rămâne niciodată o ciornă cu
                # alte sume decât statul afișat.” Ciorna nevalidată (în afara cozii sau la validare) se compară cu nota din statul de
                # acum, după amprentă (data + liniile): aceeași -> rămâne; alta -> se înlocuiește (elementul ei din coadă cade prin
                # `trg_coada_nota_sincron`, iar notificarea „de validat” se rezolvă „înlocuită”).
                from core import note_derivate as _nd
                from core import coada_api as _cq
                if not _nd.respinsa(cur, schema, r[0]):
                    if not _nd.ciorna_nevalidata(cur, schema, r[0]):
                        return {**p, "deja_contata": True, "nota_id": r[0], "cod": "DEJA_CONTATA"}
                    ciorna_veche = r[0]
                    repo_contabilitate.punct_de_revenire(cur, "salarii_ciorna")
                else:
                    _vechi, _motiv = _cq.amprente_note(cur, [r[0]]), _cq.motiv_respingere(cur, schema, r[0])   # [S3]
                    _nd.sterge_respinsa(cur, schema, r[0])
                    inlocuita = r[0]
            # Statusul e PARAMETRU, nu text in SQL: asa se poate asertaza pe structura ca nota
            # intra CIORNA (patru-ochi), nu cautand `'ciorna'` intr-un sir (METODA §23).
            # [lotul 07.10 pct.13] descrierea = ce înregistrează nota; documentul = statul de plată, din sursa unică a notelor
            # automate (`jurnal_api.eticheta_document`: fel, număr, dată). Forma veche le scria pe amândouă „Stat de plat(a|ă)
            # LL/AAAA”, iar eticheta din coadă le lipea: „Stat de plata 11/2026 · Stat de plată 11/2026”.
            # [lotul 11, 451] antetul din sursa unică `salarii_contare.antet_nota` — aceeași cu regenerarea pe uscat a ciornei
            # (`ciorne_depasite`), ca nota scrisă și cea comparată la validare să nu poată spune lucruri diferite
            _data, _nr, _descr, _doc = _sc.antet_nota(an, luna)
            nota_id = repo_contabilitate.nota_cu_sursa_si_status(cur, _data, _nr, _descr, "salarii", _uc_comun.STARE_CIORNA, _doc)[0]
            for n in p["note"]:   # [lotul 13, 536] rândurile de cheltuială cu centrul salariaților lor
                repo_contabilitate.adauga_linie_fara_schema(cur, nota_id, n["debit"], n["credit"], n["suma"], n.get("centru_cost_id"))
            if ciorna_veche:
                if _cq.amprente_note(cur, [ciorna_veche]) == _cq.amprente_note(cur, [nota_id]):
                    repo_contabilitate.revino_la(cur, "salarii_ciorna")   # aceleași sume și dată: ciorna e chiar statul afișat
                    return {**p, "deja_contata": True, "nota_id": ciorna_veche, "cod": "DEJA_CONTATA"}
                _nd.sterge_ciorna_inlocuita(cur, schema, ciorna_veche)
            if inlocuita:
                # [S3] recontabilizarea care scrie ACEEAȘI notă ca cea respinsă cere confirmare explicită (nu se blochează)
                _av = _cq.avertisment_neschimbata(_vechi, _cq.amprente_note(cur, [nota_id]), _motiv, confirma)
                if _av:
                    conn.rollback()
                    return {**p, **_av, "deja_contata": True, "nota_id": inlocuita}
        conn.commit()
    if inlocuita:
        return {**p, "deja_contata": True, "nota_id": nota_id, "nota_inlocuita": inlocuita, "cod": "INLOCUITA"}
    if ciorna_veche:   # [retest 08.10 pct.1] ciorna cu alte sume a fost înlocuită de nota din statul de acum
        return {**p, "deja_contata": True, "nota_id": nota_id, "nota_inlocuita": ciorna_veche, "cod": "CIORNA_INLOCUITA"}
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
        raise _erori.DateInvalide(f"fișierul de la casa de marcat nu se poate citi: {e}")
    if not rz["data"]:
        raise _erori.DateInvalide("nu s-a putut extrage data din idR")
    if not rz.get("nr_bonuri") or rz["nr_bonuri"] <= 0:
        # D394 lit.G (OPANAF 2194/2025 pct.14): numărul de bonuri al lunii — un Z fără el n-are ce declara
        raise _erori.DateInvalide(MESAJ_AMEF_FARA_BONURI)
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                iid = repo_contabilitate.nota_amef_ciorna(cur, schema, rz["data"], _numar_z, _jurnal_api.explicatie_raport_z(rz["data"], rz["nui"], rz["nr_raport"], rz["nr_bonuri"], amef=True),
                                                          _jurnal_api.eticheta_document("Raport Z", rz["nr_raport"], rz["data"], "AMEF %s" % rz["nui"]))[0]
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
            # [lot 19 pct.4b] defalcarea pe cote, cum o dă casa (OPANAF 146/2018 sect. II.7 `coteZ`: valOp = valoarea
            # operațiunilor cu TVA, tva = TVA-ul cotei) -> D300 rd.9/10 o citește de aici (nota n-o poate purta).
            for cota in rz["cote"]:
                if cota["valoare"] or cota["tva"]:
                    repo_contabilitate.adauga_z_cota(cur, schema, iid, D(str(cota["cota"])),
                                                     cota["valoare"] - cota["tva"], cota["tva"])
            # [D394 op2 Î1, decizia B] casa + bonurile, în ACELAȘI rând ca la ruta tastată (o singură sursă pt D394)
            repo_contabilitate.adauga_z_amef(cur, schema, iid, rz["nui"], rz["nr_bonuri"])
            from core import eticheta_nota as _et   # [258] nota numită ca în Registrul jurnal (nu prin id)
            _eticheta = _et.nota(cur, schema, iid)
            _rip = _z_in_rip(conn, cur, schema, rz["data"], rz["nr_raport"], rz["nui"], numerar, ctx)   # [368] la PFA: registrul
        conn.commit()
    if _rip is not None:
        return {"registru": "rip", "rip_id": _rip.get("id"), "data": rz["data"], "total": str(rz["total"]), "tva_total": str(rz["total_tva"]),
                "cote": [{"cota": x["cota"], "tva": str(x["tva"])} for x in rz["cote"]], "numerar": str(numerar), "card_altele": str(rest)}
    return {"inregistrare_id": iid, "nota_eticheta": _eticheta, "status": "ciorna", "data": rz["data"],
            # [lotul 10, comanda 10.2 pct.8c, clasa] conturile notei scrise, ca la Z-ul tastat
            "linii": [{"debit": deb, "credit": cred, "suma": str(suma)} for deb, cred, suma in linii],
            "total": str(rz["total"]), "tva_total": str(rz["total_tva"]),
            "cote": [{"cota": x["cota"], "tva": str(x["tva"])} for x in rz["cote"]],
            "numerar": str(numerar), "card_altele": str(rest)}



def _z_in_rip(conn, cur, schema, data, nr_raport, nui, numerar, ctx):
    """[deficiența 368, retestul 19.10.2026: „Raport Z la PFA spune «Încasări zilnice → notă automată» — la PFA nu există note contabile.”]
    La partidă simplă evidența e registrul de încasări și plăți (OMFP 170/2015): numerarul Z-ului intră acolo, ca încasare din activitate
    (ciornă, de validat, ca orice operațiune). Cardul se înregistrează când banii ajung în cont, din extrasul de bancă („Import din bancă”),
    altfel s-ar număra de două ori. Nota rămâne purtătorul intern al TVA-ului pe cote (D300 rd.9/10, D394) — la PFA ea nu apare în niciun
    registru. -> {"id": ...} (operațiunea, sau {} fără numerar) la PFA; None la partidă dublă. Aceeași regulă la Z-ul scris și la AMEF."""
    from core import z_descarcare as _zd_rip   # [lotul 12, C139] formatul unic al încasării Z (ștergerea la PFA o găsește după el)
    from core.migrare_api import regim_contabil as _regim
    repo_contabilitate.search_path_firma(cur, schema)
    pf = repo_firma_profil.profil_fiscal(cur)
    if not pf or _regim(pf[0]) != "simpla":
        return None
    if not numerar:
        return {}
    from core import rip_api as _rip_api
    r = _rip_api.adauga(conn, schema, {"data_operatiune": str(data)[:10], "tip": "incasare", "document_tip": "raport Z",
                                       "document_numar": nr_raport, "document_data": str(data)[:10],
                                       "explicatie": _zd_rip.EXPLICATIE_RIP % (nr_raport, nui),
                                       "suma": numerar, "metoda": "numerar", "categorie": "activitate"}, user_id=int(ctx["uid"]))
    if r.get("eroare"):
        raise _erori.DateInvalide(r["eroare"])
    return r


def horeca_raport_z(tenant_id, rz, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/horeca/raport-z`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal as D
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, rz.data)   # [R42 (a)] nota poartă data raportului Z
        nui = (rz.nui or "").strip()
        nr_raport = (rz.nr_raport or "").strip()
        if not nui or not nr_raport:
            raise _erori.CerereGresita(MESAJ_Z_FARA_CHEIE)
        if not rz.nr_bonuri or rz.nr_bonuri <= 0:
            raise _erori.CerereGresita(MESAJ_Z_FARA_BONURI)
        numar = "Z-%s-%s" % (nui, nr_raport)
        total = D(str(rz.total_11)) + D(str(rz.total_21))
        if total <= 0:
            raise _erori.CerereGresita("totalul pe cote trebuie să fie pozitiv")
        # [lotul 10, comanda 10.2 pct.8b] refuzul spune cifrele (total, încasat, diferența); comparația pe sumele în lei, în Decimal
        from decimal import ROUND_HALF_UP as _RHU
        if total.quantize(D("0.01"), rounding=_RHU) != (D(str(rz.numerar or 0)) + D(str(rz.card or 0))).quantize(D("0.01"), rounding=_RHU):
            from core import raport_z as _rz
            raise _erori.CerereGresita(_rz.mesaj_plata_diferita(total, rz.numerar, rz.card))
        # suta marita: TVA = total * cota / (100 + cota). [lot 19 pct.4b] Cotele din COTE la data raportului (CF art.291
        # alin.(1)-(2): standard / redusă), nu 11 și 21 scrise aici; rotunjirea ARITMETICĂ (ROUND_HALF_UP) — un
        # `quantize` fără `rounding` e bancar (half-even) și dă alt TVA pe ,005 exact (CLAUDE.md „Rotunjire fiscală”).
        from datetime import date as _date
        _dz = _date.fromisoformat(str(rz.data)[:10])
        c_red = _common.cota("tva_redusa", _dz)[0] * 100
        c_std = _common.cota("tva_standard", _dz)[0] * 100
        tva11 = (D(str(rz.total_11)) * c_red / (100 + c_red)).quantize(D("0.01"), rounding=_RHU)
        tva21 = (D(str(rz.total_21)) * c_std / (100 + c_std)).quantize(D("0.01"), rounding=_RHU)
        baza11 = D(str(rz.total_11)) - tva11
        baza21 = D(str(rz.total_21)) - tva21
        with conn.cursor() as cur:
            _uc_comun._cere_z_unic(cur, schema, numar)
            # [decizii 07.10 pct.3] „Raportul Z la cantitativ-valoric: fără refuz. Descărcarea pe articol se cere explicit (manual sau
            # prin rețetă); Z-ul nu se validează fără ea.” -> la cantitativ-valoric nota intră CIORNĂ (validarea o păzește)
            from core import metoda_stoc as _ms
            _la_cost = _ms.citeste(cur, schema) == _ms.CV
            _desc_z = _jurnal_api.explicatie_raport_z(rz.data, nui, nr_raport)   # [lotul 13, 618] data românească, sursa unică
            _doc_z = _jurnal_api.eticheta_document("Raport Z", nr_raport, rz.data, "casa %s" % nui)
            # [lotul 10, C73 / U2] cursa dintre două cereri cu același Z trecea de verificarea de mai sus și cădea cu 500 pe indexul
            # `inregistrari_raport_z_unic`; acum ACELAȘI 409 ca a doua încercare conștientă (ca la import-amef), prin helperul comun
            from core import raport_z as _raport_z
            with _chei.refuza_dublura(cur, (_raport_z.NUME_INDEX,), lambda cur, e: _uc_comun._cere_z_unic(cur, schema, numar)):
                iid = repo_contabilitate.nota_horeca_z_ciorna(cur, schema, rz.data, numar, _desc_z, _doc_z)[0]   # [§6 pct.7, R36]
            linii = []
            if rz.numerar: linii.append(("5311", "707", rz.numerar))
            if rz.card: linii.append(("5125", "707", rz.card))
            # corectie TVA: 707 -> 4427 pentru TVA colectata
            tva_total = tva11 + tva21
            if tva_total: linii.append(("707", "4427", float(tva_total)))
            for deb, cre, suma in linii:
                repo_contabilitate.adauga_linie_3(cur, schema, iid, deb, cre, suma)
            # [lot 19 pct.4b] defalcarea pe cote -> D300 rd.9/10 (nota contabilă poartă un singur TVA, fără cotă)
            for _c, _b, _t in ((c_red, baza11, tva11), (c_std, baza21, tva21)):
                if _b or _t:
                    repo_contabilitate.adauga_z_cota(cur, schema, iid, _c, _b, _t)
            # [D394 op2 Î1, decizia B] casa + bonurile, în ACELAȘI rând ca la importul AMEF (o singură sursă pt D394)
            repo_contabilitate.adauga_z_amef(cur, schema, iid, nui, int(rz.nr_bonuri))
            from core import eticheta_nota as _et   # [258] nota numită ca în Registrul jurnal (nu prin id)
            _eticheta = _et.nota(cur, schema, iid)
            _rip = _z_in_rip(conn, cur, schema, rz.data, nr_raport, nui, rz.numerar, ctx)
    if _rip is not None:
        return {"ok": True, "registru": "rip", "rip_id": _rip.get("id"), "numerar": float(rz.numerar or 0),
                "card": float(rz.card or 0), "tva_11": float(tva11), "tva_21": float(tva21),
                "baza_11": float(baza11), "baza_21": float(baza21)}
    # [lotul 10, comanda 10.2 pct.8c] „După generare […] conturile notei nu se văd” -> rândurile notei scrise, cu conturile și suma
    return {"ok": True, "nota_id": iid, "nota_eticheta": _eticheta, "descarcare_pe_articol": _la_cost,
            "linii": [{"debit": deb, "credit": cre, "suma": str(D(str(suma)).quantize(D("0.01"), rounding=_RHU))} for deb, cre, suma in linii],
            "tva_11": float(tva11), "tva_21": float(tva21),
            "baza_11": float(baza11), "baza_21": float(baza21)}



def horeca_rapoarte_z(tenant_id, an, luna, ctx):
    """[decizii 07.10 pct.3] Corpul rutei `GET /tenants/{tenant_id}/horeca/rapoarte-z`: rapoartele Z ale lunii, cu descărcarea."""
    _uc_comun._cere_perioada(an, luna)
    from core import z_descarcare as _zd, metoda_stoc as _ms
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            metoda = _ms.citeste(cur, schema)
        return {"rapoarte": _zd.lista_luna(conn, schema, an, luna), "descarcare_pe_articol": metoda == _ms.CV}


def horeca_z_fara_marfa(tenant_id, nota_id, corp, ctx):
    """[decizii 07.10 pct.3] Corpul rutei `POST /tenants/{tenant_id}/horeca/raport-z/{nota_id}/fara-marfa`: {fara_marfa: true}
    declară explicit că Z-ul n-a vândut marfă din stoc; {fara_marfa: false} retrage declarația."""
    from core import z_descarcare as _zd
    if not isinstance(corp.get("fara_marfa"), bool):
        raise _erori.CerereGresita("Spune explicit dacă raportul Z e fără marfă din stoc (da / nu).")
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn(schema) as conn:
        try:
            return _zd.marcheaza_fara_marfa(conn, schema, nota_id, corp["fara_marfa"])
        except ValueError as e:
            raise _erori.DateInvalide(str(e))


def tenant_fluturas(tenant_id, salariat_id, an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/fluturas/{salariat_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import stat_plata_api as _sp
    _uc_comun._cere_perioada(an, luna)
    with db.get_conn() as conn:  # [search_path_tenant_v1] schema + nume firma pe conn public
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
        try:
            emise = _spe.emite(conn, schema, an, luna, de_cine=str(ctx["uid"]))
        except _chei.CheieDublata as e:   # [lotul 10, C73] emis între timp de altă cerere -> 409 numit, nu 500
            raise _erori.Conflict(e.detaliu())
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
        raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        d = tenant_provisioning.detalii_tenant(conn, tenant_id)
    with db.get_conn(schema) as conn:  # balanta_pdf foloseste nume necalificate -> search_path pe tenant
        pdf = documente_api.balanta_pdf(conn, schema, an, luna, (d or {}).get("nume") or "")
    return pdf



def banca_rec_import(tenant_id, continut, nume_fisier, ctx, confirma_cont=False):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/banca/reconciliere/import`; docstringul ei a ramas in stratul HTTP."""
    from core import banca_parser, banca as _bk, reconciliere_api as _rec
    try:
        extras = banca_parser.citeste_extras(continut, nume_fisier or "")
    except Exception as e:
        raise _erori.CerereGresita(f"nu s-a putut citi extrasul: {e}")
    tranzactii = extras["tranzactii"]
    for t in tranzactii:
        r = _bk.regula_cont({"sens": "debit" if t["suma"] < 0 else "credit",
                             "suma": abs(t["suma"]), "descriere": t.get("detalii", "")})
        t["cui"], t["tip"], t["nota"], t["tip_detectat"] = r.get("cui"), r.get("tip"), r.get("nota"), r.get("tip_detectat")
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        # [16.10.2026, lotul 6, 277 / 276b] liniile noi + cele găsite deja (aceeași mișcare), apoi soldurile extrasului față de 5121
        rez = _rec.importa_extras(conn, schema, tranzactii, nume_fisier or "", continut, cont=extras["cont"],
                                  cont_confirmat=bool(confirma_cont))   # [lotul 12, C121] extrasul altui cont: confirmat de contabil
        rez["solduri"] = _rec.compara_solduri(conn, schema, extras["sold_initial"], extras["sold_final"])
        return _uc_comun._raspuns(rez)



def contracte_genereaza(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/contracte/genereaza`; docstringul ei a ramas in stratul HTTP."""
    from core import contracte_api as _ct
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        return _uc_comun._jurnal_rez(_j.creeaza(conn, schema, corp.get("descriere"), corp.get("data"), corp.get("linii"),
                                                corp.get("document_ref")))



def jurnal_editeaza(tenant_id, nota_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        # [lotul 07.10 pct.5] data se poate corecta din editor: luna NOUĂ trebuie și ea să fie deschisă (o notă nu se mută
        # într-o lună închisă — R42 (a), aceeași poartă ca la creare)
        if corp.get("data"):
            _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        return _uc_comun._jurnal_rez(_j.editeaza(conn, schema, nota_id,
                                       corp.get("descriere"), corp.get("data"), corp.get("linii"),
                                       corp.get("document_ref")))



def jurnal_sterge(tenant_id, nota_id, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/jurnal/{nota_id}`; docstringul ei a ramas in stratul HTTP."""
    from core import jurnal_api as _j
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
    from core import coada_api as _cq
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        rez = _cq.valideaza_documentul(conn, schema, nota_id)   # [lotul 12, C107] notele documentului se validează împreună, ca în coadă
        if isinstance(rez, dict) and rez.get("ok"):
            _aplica_reevaluarea(conn, schema, nota_id)
        return _uc_comun._jurnal_rez(rez)


def jurnal_depasita(tenant_id, nota_id, ctx):
    """[lotul 11, deficiența 451] Corpul rutei `GET /tenants/{tenant_id}/jurnal/{nota_id}/depasita`: ciorna e depășită (regenerarea pe uscat
    dă altă notă decât cea scrisă)? Aceeași verificare ca la validare (`ciorne_depasite.verifica`), numai citire — o folosește „De
    validat” ca să ofere refacerea după un refuz. {"depasita": bool, ...detaliul refuzului}."""
    from core import ciorne_depasite as _cd
    from psycopg2.extras import RealDictCursor
    with db.get_conn() as conn:
        # accesul de lucru (ca validarea și refacerea pe care le servește), nu poarta de citire istorică
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            d = _cd.verifica(conn, cur, schema, nota_id)
        conn.rollback()   # citire: regenerarea pe uscat nu scrie nimic
    return {"depasita": bool(d), **(d or {})}


def jurnal_reface(tenant_id, nota_id, ctx):
    """[lotul 11, deficiența 451] Corpul rutei `POST /tenants/{tenant_id}/jurnal/{nota_id}/reface`: ciorna depășită se reface din SURSA ei, pe
    drumul care o scrie (nicio regulă paralelă): statul de plată -> „Contabilizează statul” (`salarii_contare_scrie`), amortizarea ->
    „Generează amortizarea” (`tenant_amortizare`), mișcarea de stoc -> `stocuri_cv_api.reface_nota_miscare`, contarea facturii emise ->
    `ciorne_depasite.reface_factura_emisa` (`contare_facturi.contabilizeaza`). Ciorna veche e înlocuită; nota
    nouă intră ciornă (o validează omul). O ciornă la zi nu se reface (refuz numit)."""
    from core import ciorne_depasite as _cd
    from psycopg2.extras import RealDictCursor
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_perioada_deschisa(conn, schema, nota_id)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            d = _cd.verifica(conn, cur, schema, nota_id)
            fel = _cd.felul(cur, schema, nota_id)
            al = _cd.an_luna(cur, schema, nota_id)
        if not d:
            conn.rollback()
            raise _erori.CerereGresita("Nota e la zi cu sursa ei (sau nu e o ciornă derivată pe care aplicația o poate reface): nu e nimic "
                                       "de refăcut — o poți valida.")
        if d["neregenerabila"]:
            conn.rollback()
            raise _erori.CerereGresita(d["mesaj"])
        nou = None
        if fel in ("stoc_iesire", "stoc_retur"):
            from core import stocuri_cv_api as _cva
            nou = _cva.reface_nota_miscare(conn, schema, nota_id)["nota_id"]
            conn.commit()
        elif fel == "factura_emisa":   # [lotul 11, 451, S2] contarea facturii emise, refăcută din factura de acum (`contabilizeaza`)
            try:
                nou = _cd.reface_factura_emisa(conn, schema, nota_id)
            except ValueError as e:
                conn.rollback()
                raise _erori.CerereGresita(str(e))
            conn.commit()
        else:
            conn.rollback()
            if fel not in ("salarii", "amortizare"):   # un fel REGENERAT fără refacere aici n-ar reface nimic, dar ar spune „refăcută”
                raise _erori.CerereGresita("Nota nu se poate reface din aplicație (%s): corectează sursa ei." % fel)
    if fel == "salarii":
        nou = salarii_contare_scrie(tenant_id, al[0], al[1], ctx).get("nota_id")
    elif fel == "amortizare":
        nou = tenant_amortizare(tenant_id, al[0], al[1], ctx).get("nota_id")
    from core import eticheta_nota as _et
    with db.get_conn() as conn, conn.cursor() as cur:
        et = _et.nota(cur, schema, nou) if nou else None
    return {"ok": True, "nota_id": nou, "nota_veche": nota_id, "nota_eticheta": et,
            "mesaj": "Nota a fost refăcută din %s: o ciornă nouă (%s), de validat." % (d["sursa"], et or "nota nouă")}


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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                                 "care există în calendar — s-a primit %r și %r."
                                 % (data_start, data_end))
    # [lotul 6] Un interval INVERSAT producea un XML SAF-T, adica un fisier oficial despre o
    # perioada care nu exista. Raportul se cere pe un interval, iar un interval are o ordine.
    if de < ds:
        raise _erori.DateInvalide("Sfârșitul perioadei (%s) e înaintea începutului (%s). "
                                 "Raportul se cere pe un interval, iar intervalul are o ordine."
                                 % (data_ro(de), data_ro(ds)))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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



def _factura_importata(cur, schema, f):
    """[lotul 11, C79] Factura din XML (`efactura_import.parseaza_xml`): `_factura_din_parsat` (facturi + linii, dedup) ȘI TVA-ul ei pe
    cote, cum l-a scris furnizorul (BG-23, `factura_tva_cote`) — de pe el se contează și se declară TVA-ul (CF art.299 alin.(1) lit.a,
    art.319 alin.(20) lit.j), nu din baze recalculate. Singurul drum prin care importul introduce o factură (garda:
    `core/test_lot11_y_tva_primita.py::test_importul_trece_numai_prin_factura_importata`). (factura_id, creat_nou)."""
    fid, nou = _uc_comun._factura_din_parsat(cur, schema, f)
    repo_efactura.salveaza_tva_cote(cur, schema, fid, f.get("tva_cote"))
    # [lotul 11, C83] factura în valută: cursul BNR al operațiunii (CF art.290 alin.(2), HG 1/2016 pct.35 alin.(1)) și sumele în lei, cum le
    # pune emiterea — BT-111 când XML-ul îl are. Cursul l-a adus apelantul înaintea tranzacției (`_preincalzeste_cursul`); un refuz (BNR
    # indisponibil) lasă factura fără curs, iar contarea îl reîncearcă (`contare_facturi.contabilizeaza`)
    from core import contare_facturi as _cf
    _cf.curs_factura_importate(cur, schema, {"id": fid, "moneda": f.get("moneda"), "curs_bnr": None, "xml": f.get("xml"),
                                             "data_emitere": f.get("data_emitere"), "total": f.get("total"), "tva": f.get("tva")})
    return fid, nou


def factura_primita_valideaza(tenant_id, primita_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/facturi-primite/{primita_id}/valideaza`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    # [deficiența 418a] statutul furnizorului se află din XML și ANAF, nu de la contabil: citirea scurtă a facturii, apoi ANAF cu
    # conexiunea închisă; ce nu se poate afla (ANAF jos, XML fără BT-31) rămâne pe alegerea contabilului
    statut, f0 = {"platitor_tva": None, "tva_la_incasare": None}, None
    with db.get_conn() as conn0:
        schema0 = auth_api.schema_tenant(conn0, ctx["uid"], tenant_id)
        if schema0:
            with conn0.cursor() as cur0:
                r0 = repo_efactura.primita_pentru_validare(cur0, schema0, primita_id)
            try:
                f0 = _ef.parseaza_xml((r0[1] or "").encode("utf-8"), r0[2]) if r0 and r0[1] else None
            except Exception:  # noqa: BLE001 — XML-ul necitibil e refuzat mai jos, cu motivul
                f0 = None
    if f0:   # [lotul 11, C83] cursul BNR al facturii în valută, adus înaintea tranzacției (`_factura_importata` îl pune pe factură)
        _uc_comun._preincalzeste_cursul(f0.get("moneda"), f0.get("data_emitere"))
    if f0 and f0.get("data_emitere"):
        from core import anaf_api as _anaf
        _cif0, _d0 = f0.get("tert_cui"), str(f0["data_emitere"])   # la factura primită, terțul e furnizorul
        statut = _anaf.statut_furnizori([(_cif0, _d0, f0.get("furnizor_cod_tva"))])[(_cif0, _d0)]
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        with conn.cursor() as cur:
            r = repo_efactura.primita_pentru_validare(cur, schema, primita_id)
            if not r:
                raise _erori.Inexistent("factură primită inexistentă")
            status, xmlb, cifb, fid_ex = r
            if status == "validata":          # idempotent - nu crea a doua cheltuiala
                return {"stare": "deja_validata", "factura_id": fid_ex}
            if status == "respinsa":
                raise _erori.Conflict("factura a fost respinsă; nu se poate valida")
            from core import uc_factura_primita as _ufp
            _ufp.cont_facturii(conn, schema, corp, primita_id)   # [FFF1] contul, înaintea citirii XML-ului (aceeași ordine ca înainte de 477)
            try:
                f = _ef.parseaza_xml((xmlb or "").encode("utf-8"), cifb)
                # [lotul 12, C120, clasa 599] factura între alte două firme nu se validează nici dacă a ajuns deja în lista „de validat”
                # (din SPV sau dintr-un import de dinainte de reparație): confruntarea cu CUI-ul din Date firmă, ca la import
                _rand_cui = repo_firma_profil.cui_firma_3(cur, schema)
                refuz = _ef.alta_firma(f, _rand_cui[0] if _rand_cui else None)
            except Exception as e:
                refuz = "XML-ul nu se poate citi: %s" % str(e)[:200]
            if refuz:   # un singur refuz: XML-ul necitibil nu mai are ce confrunta
                raise _erori.DateInvalide(refuz)
        # [lotul 12, 477] restul actului (clasificarea, nota, gestiunea, anunțul cursului) e ACELAȘI pentru factura din XML și pentru cea
        # introdusă de mână: `uc_factura_primita.valideaza` (tipul furnizorului [273], categoria art.331, ... — mutate acolo)
        return _ufp.valideaza(conn, schema, f, corp, statut, primita_id=primita_id)



def operatiuni_date(tenant_id, ce, parametri, ctx):
    """[lotul 13] Corpul rutei `GET /tenants/{tenant_id}/operatiuni-date?ce=…`: listele din care formularele Operațiunilor aleg ce
    aplicația are deja (deficiența 511, „Aplicația cere de mână date pe care le are”), în loc să fie scrise de mână. Nu scrie nimic.
      ce=facturi_valuta (`tip` creanta|datorie, `data`) — facturile în valută deschise, cu soldul rămas și cursul de evidență (524);
      ce=articole (`tip` produs|marfa) — articolele de stoc pe 345 / 371, cu stocul, unitatea și CMP-ul (510 / 548)."""
    from datetime import date as _date
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    try:
        data = _date.fromisoformat(str(parametri.get("data") or "")[:10]) if parametri.get("data") else _common.azi_ro()
    except ValueError:
        raise _erori.DateInvalide("Data nu e o dată calendaristică (aaaa-ll-zz): %r." % parametri.get("data"))
    with db.get_conn(schema) as conn:
        with conn.cursor() as cur:
            if ce == "facturi_valuta":
                from core import ops_valuta as _ov
                tip = parametri.get("tip")
                if tip not in ("creanta", "datorie"):
                    raise _erori.DateInvalide(nomenclator_cerut("tip", "creanta|datorie"))
                out = [{"id": f["id"], "document": f["document"], "partener": f["partener"], "moneda": f["moneda"],
                        "rest_valuta": str(f["rest_valuta"]), "curs_evidenta": str(f["curs_evidenta"]), "curs_din": f["curs_din"],
                        "cont_tert": f["cont_tert"]}
                       for f in _ov.facturi_deschise(cur, schema, "emisa" if tip == "creanta" else "primita", data)]
                return {"facturi": out}
            if ce == "articole":   # [lotul 13, 510 / 548] bunurile din stoc din care se alege: produse finite (345) / mărfuri (371)
                from core import stocuri_cv_api as _cva
                cont = {"produs": "345", "marfa": "371"}.get(parametri.get("tip"))
                if not cont:
                    raise _erori.DateInvalide(nomenclator_cerut("tip", "produs|marfa"))
                return {"articole": [{"id": a["id"], "denumire": a["denumire"], "um": a["um"], "stoc": a["stoc"], "cmp": a["cmp"]}
                                     for a in _cva.articole(conn, schema) if str(a["cont_stoc"] or "").startswith(cont)]}
            if ce == "obiecte":   # [lotul 13, 508] obiectele de inventar în starea cerută (magazie / folosinta)
                stare = parametri.get("tip")
                out = []
                for oid, den, val, din, dare, scos, st_i, st_d, fid in repo_operatiuni.obiecte_inventar(cur, schema):
                    ok = (stare == "magazie" and dare is None and scos is None and (st_i == "validata" or fid is not None)) or \
                         (stare == "folosinta" and dare is not None and st_d == "validata" and scos is None)
                    if ok:
                        out.append({"id": oid, "denumire": den, "valoare": str(val), "data": str(din)})
                return {"obiecte": out}
            if ce == "facturi_neincasate":   # [lotul 13, 511] facturile emise neîncasate, cu soldul și scadența
                from core import reconciliere_api as _rec
                fs = [f for f in _rec.facturi_deschise_detalii(conn, schema) if f["directie"] == "emisa"]   # [lotul 13] cu partenerul și numărul (detaliile)
                scad = repo_operatiuni.scadente_facturi(cur, schema, [f["id"] for f in fs])
                from core.pdf_util import serie_nr as _serie_nr   # [443] seria și numărul separat („F1 nr. 3”), ca peste tot
                return {"facturi": [{"id": f["id"], "document": _serie_nr(f.get("serie"), f["numar"]), "partener": f["tert_nume"],
                                     "sold": f["sold"], "scadenta": str(scad.get(f["id"]) or ""),
                                     "zile": (data - scad[f["id"]]).days if scad.get(f["id"]) else None} for f in fs]}
            if ce == "conturi_trezorerie":   # [lotul 13, decizia după 524 / 504] contul decontării în valută, din planul firmei
                return {"conturi": [{"id": c, "cont": c, "denumire": d} for c, d in conturi_trezorerie_decontare(cur, schema)]}
            if ce == "catalog":   # [lotul 13, 521] codul din Catalogul HG 2139/2004: denumirea și plaja duratei
                from core import mf_registru as _mfr
                cod = str(parametri.get("tip") or "").strip().rstrip(".")
                c = _mfr.catalog().get(cod)
                return {"cod": cod, "gasit": bool(c), **({"denumire": c["denumire"], "ani_min": c["ani_min"], "ani_max": c["ani_max"]}
                                                        if c else {})}
    raise _erori.DateInvalide(nomenclator_cerut("ce", "facturi_valuta|articole|obiecte|facturi_neincasate|catalog|conturi_trezorerie"))


#: [lotul 13, decizia Costin după 524 / 504] Conturile de trezorerie prin care se decontează o creanță / datorie în valută: 5124 „Conturi
#: la bănci în valută”, 5121 „Conturi la bănci în lei” (banca a convertit), 5314 „Casa în valută” (planul de conturi, OMFP 1802/2014) și
#: analiticele lor din planul firmei (un procesator de plăți ținut ca analitic al unuia dintre ele) — o listă ÎNCHISĂ, fără nimic ales
CONTURI_TREZORERIE_DECONTARE = ("5124", "5121", "5314")


def conturi_trezorerie_decontare(cur, schema):
    """[(simbol, denumire)] — contul de trezorerie al decontării în valută se alege numai dintre acestea."""
    return repo_operatiuni.conturi_cu_prefix(cur, schema, CONTURI_TREZORERIE_DECONTARE)


def decontare_valuta(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/decontare-valuta`; docstringul ei a ramas in stratul HTTP.

    [lotul 13, deficiența 524] Decontarea se face pe FACTURA din care provine creanța / datoria (`ops_valuta.facturi_deschise`): moneda,
    contul de terț, partenerul și cursul de evidență (al facturii sau al ultimei reevaluări validate) vin din evidență, nu se scriu; suma
    în valută nu poate depăși soldul rămas al facturii. Cursul decontării e cursul BNR al zilei (CF art.290 alin.(2)), ca înainte. Nota
    se leagă de factură (soldul ei scade), cu partenerul pe rândul contului de terț."""
    from datetime import date as _date
    from core import diferente_curs as _dc, ops_valuta as _ov
    from core import curs_bnr as _cb
    # [lotul 13, reparațiile finale; P5 val 3, C201] Moneda vine acum din factură (524), deci cursul se aduce după o citire SCURTĂ a monedei
    # și ÎNAINTEA tranzacției — descărcarea BNR (până la 3×10 s) nu ține o conexiune din pool (ca `factura_contabilizeaza`).
    _md = None
    if str(corp.get("factura_id") or "").isdigit():
        with db.get_conn() as conn0:
            schema0 = auth_api.schema_tenant(conn0, ctx["uid"], tenant_id)
            with conn0.cursor() as cur0:
                _md = repo_efactura.moneda_si_data(cur0, schema0, int(corp["factura_id"])) if schema0 else None
    if _md:
        _uc_comun._preincalzeste_cursul(_md[0], corp.get("data"))
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            _uc_comun._campuri_lipsa(corp, ("data", "tip", "factura_id", "valoare_valuta", "cont_banca"))   # [lotul 11, 440 / A4]
            if corp.get("tip") not in ("creanta", "datorie"):
                raise ValueError(nomenclator_cerut("tip", "creanta|datorie"))
            data = _date.fromisoformat(str(corp["data"])[:10])
            with conn.cursor() as cur:
                f = _ov.factura_deschisa(cur, schema, corp["factura_id"], "emisa" if corp["tip"] == "creanta" else "primita", data)
            if not f:
                raise _erori.DateInvalide({"mesaj": "Factura aleasă nu e o %s în valută deschisă la %s (contată prin notă validată, cu sold "
                                                    "rămas). Alege-o din listă." % ("creanță" if corp["tip"] == "creanta" else "datorie",
                                                                                     data_ro(data)),
                                           "erori_campuri": [{"camp": "op-factura_id", "mesaj": "Alege factura din listă."}]})
            v = Decimal(str(corp["valoare_valuta"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if v <= 0 or v > f["rest_valuta"]:
                m = ("Suma de %s %s depășește soldul rămas al facturii %s: %s %s. O decontare peste sold ar înregistra o %s care nu "
                     "există (și o diferență de curs inventată)." % (bani(v), f["moneda"], f["document"], bani(f["rest_valuta"]), f["moneda"],
                                                                      "creanță" if corp["tip"] == "creanta" else "datorie")) if v > 0 \
                    else "Suma în valută trebuie să fie un număr pozitiv."
                raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-valoare_valuta", "mesaj": m}]})
            try:
                curs_dec, _dcurs, _sursa = _cb.curs_pentru(conn, f["moneda"], data)
            except _cb.MonedaNecotata as _mn:   # [lotul 8] iesea ca `500`
                raise _erori.DateInvalide(str(_mn))
            except _cb.CursIndisponibil as _ci:
                raise _erori.Conflict(str(_ci))
            cont_tr = _cv.cere_cont(conn, schema, corp.get("cont_banca"), "cont_banca")
            with conn.cursor() as cur:
                permise = [x[0] for x in conturi_trezorerie_decontare(cur, schema)]
            if cont_tr not in permise:
                m = ("Contul %s nu e un cont de trezorerie al decontării: alege din listă — %s (conturile 5124, 5121, 5314 și analiticele "
                     "lor din planul firmei)." % (cont_tr, ", ".join(permise) or "planul firmei nu are niciunul"))
                raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": "op-cont_banca", "mesaj": m}]})
            r = _dc.nota_decontare(v, f["curs_evidenta"], curs_dec, corp["tip"], f["cont_tert"], cont_tr)
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        d = r["diferenta"]
        descr = (corp.get("descriere") or ("Decontare %s %s" % ("încasare" if corp["tip"] == "creanta" else "plată", f["document"]))) + \
            f" {bani(v)} {f['moneda']} curs {curs_dec} (evidență {f['curs_evidenta']}, {f['curs_din']})" + \
            (f", dif. {d['sens']} {bani(d['diferenta'], 'lei')} ({d['cont']})" if d["cont"] else "")
        with conn.cursor() as cur:
            iid = repo_contabilitate.nota_operatiune_ciorna(cur, schema, corp["data"], descr[:200])[0]
            repo_operatiuni.leaga_nota_de_factura(cur, schema, iid, f["id"])   # soldul facturii scade
            from core import compensari_api as _cz
            for dd, cc, ss in r["linii"]:
                if f["cont_tert"] in (dd, cc):
                    repo_contabilitate.adauga_linie_partener(cur, schema, iid, dd, cc, ss, _cz.cui_partener(f["cui"]) or None, f["partener"])
                else:
                    repo_contabilitate.adauga_linie(cur, schema, iid, dd, cc, ss)
        conn.commit()
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "curs_decontare": str(curs_dec),
            "curs_evidenta": str(f["curs_evidenta"]), "curs_din": f["curs_din"], "factura": f["document"],
            "rest_valuta": str(f["rest_valuta"] - v), "moneda": f["moneda"],
            "lei_evidenta": str(r["lei_evidenta"]),
            "diferenta": {"suma": str(d["diferenta"]), "cont": d["cont"],
                          "sens": d["sens"]}})


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
    from core.pdf_util import serie_nr as _sn_email
    numar = _sn_email(f.get("serie"), f.get("numar"))   # [lotul 12, 443.1] „F1A nr. 14” în subiect și în text, nu „F1A14”
    firma = profil.get("nume") or ""
    subiect = "Factura %s%s" % (numar, (" - " + firma if firma else ""))
    # [C39] mesajul scris de om se escapează (rândurile lui rămân rânduri); numărul facturii la fel
    corp_html = (_common.esc(date.mesaj).replace("\n", "<br>") if date.mesaj
                  else "Bună ziua,<br><br>Atașat găsiți factura %s.<br><br>O zi bună!" % _common.esc(numar))
    html = "<div style='font-family:Arial,sans-serif;font-size:14px;color:#222'>%s</div>" % corp_html
    ok = _obs.trimite_email_html(email, subiect, html,
                                 attachments=[{"content": b64, "name": nume_pdf}])
    if not ok:
        # [lotul 12, clasa 598] eșecul canalului extern spus contabilului cu ce face, fără termeni tehnici
        raise _erori.ServiciuStrainCazut("Emailul cu factura nu a plecat acum: serviciul de email nu a răspuns. Factura rămâne emisă; "
                                         "încearcă din nou peste câteva minute sau descarcă PDF-ul și trimite-l tu.")
    return {"ok": True, "email": email}



def reges_trimite_salariat(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/reges-trimite-salariat`; docstringul ei a ramas in stratul HTTP."""
    from core import reges_client as _rg
    import uuid as _uuid
    # ── [P5 val 3, 11.09.2026] FAZA 1: citirile ─────────────────────────────────────────
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
        # [lotul 12, clasa 598] detaliul tehnic în jurnal; contabilului, ce s-a întâmplat și ce face
        _obs.esec_secundar("reges_trimite_salariat", e, alerta=True)
        raise _erori.ServiciuStrainCazut("REGES nu a răspuns, deci nu se știe dacă salariatul a ajuns acolo. Verifică în REGES înainte "
                                         "să-l trimiți din nou.")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
        _obs.esec_secundar("reges_poll", e, alerta=True)   # [lotul 12, clasa 598]
        raise _erori.ServiciuStrainCazut("REGES nu a răspuns acum la citirea răspunsurilor. Încearcă din nou peste câteva minute.")
    m_mid = _re.search(r"<(?:Initial)?MessageId>([0-9a-f-]{36})", rasp)
    m_rs = _re.search(r"ReferintaSalariat>?\s*<Id>([0-9a-f-]{36})", rasp)
    m_rc = _re.search(r"ReferintaContract>?\s*<Id>([0-9a-f-]{36})", rasp)
    # ── FAZA 2: tranzacție scurtă, necondiționat ────────────────────────────────────────
    salvat = False
    with db.get_conn() as conn:
        if m_mid:
            with conn.cursor() as cur:
                repo_salariati.scrie_raspunsul_reges(cur, rasp[:4000], m_rs.group(1) if m_rs else None, m_rc.group(1) if m_rc else None, m_mid.group(1), tenant_id)
                salvat = cur.rowcount > 0
            conn.commit()
    # [C5 clasa, comanda Costin 07.10.2026] Ecranul anunța „niciun răspuns nou” după ce mesajul fusese CONSUMAT din coada REGES și
    # scris: citea `mesaje`/`raspunsuri`, chei pe care ruta nu le-a întors niciodată. Răspunsul spune acum ce s-a întâmplat: dacă
    # a venit ceva, pentru ce mesaj, cu ce referințe și dacă s-a găsit mesajul nostru căruia să i se scrie (DS cap.27).
    return {"http_status": status, "raspuns": rasp[:1000], "primit": bool(rasp.strip()),
            "message_id": m_mid.group(1) if m_mid else None, "salvat": salvat,
            "referinta_salariat": m_rs.group(1) if m_rs else None, "referinta_contract": m_rc.group(1) if m_rc else None}



def verifica_vies_ep(tenant_id, cod_tva, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/verifica-vies`; docstringul ei a ramas in stratul HTTP."""
    from core import intracomunitar as _ic
    with db.get_conn() as conn:
        if not auth_api.schema_tenant(conn, ctx["uid"], tenant_id):
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    try:
        return _ic.verifica_vies(cod_tva)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    except Exception as e:
        _obs.esec_secundar("vies_verifica", e)   # [lotul 12, clasa 598] detaliul în jurnal, nu pe ecran
        raise _erori.ServiciuStrainCazut("Serviciul VIES al Comisiei Europene nu răspunde acum, deci codul de TVA nu s-a putut "
                                         "verifica. Încearcă din nou peste câteva minute.")



def vanzare_ic(tenant_id, corp, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/vanzare-ic`; docstringul ei a ramas in stratul HTTP."""
    from decimal import Decimal
    from core import intracomunitar as _ic
    # ── [P5 val 3, 11.09.2026] FAZA 1: citirile, fără nimic extern ──────────────────────
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
    # [lotul 8, 04.09.2026] Citirea campului era INAUNTRUL `try`-ului care prinde `Exception`,
    # deci un camp lipsa iesea ca „VIES indisponibil: 'cod_tva_client'" — o afirmatie falsa
    # despre un serviciu extern, cu numele campului intre ghilimele simple. *Ce nu s-a trimis
    # nu se afla de la VIES.*
    _cod_client = str(corp.get("cod_tva_client") or "").strip()
    # [lotul 11, deficiența 440] codul de TVA, tipul și valoarea — toate deodată, fiecare lângă câmpul ei (`op-…`), înainte de VIES
    _er = _erori.ErorileFormularului("Livrarea intracomunitară nu s-a înregistrat")
    if not _cod_client:
        _er.camp("op-cod_tva_client", "Lipsește codul de TVA al clientului. Fără el livrarea "
                                      "intracomunitară nu se poate verifica în VIES și nu ajunge "
                                      "în D390.")
    if corp.get("tip") == "bunuri":   # [C84, decizia Costin (b)] bunurile se livrează din „Emite factură” (articolul din stoc, descărcarea)
        _er.camp("op-tip", "Livrarea intracomunitară de bunuri se face din «Emite factură»: acolo alegi articolul din stoc și categoria „livrare intracomunitară”, iar marfa se descarcă din gestiune odată cu factura. Aici rămân prestările de servicii intracomunitare.")
    elif corp.get("tip") != "servicii":
        _er.camp("op-tip", nomenclator_cerut("tip", "servicii"))
    _uc_comun._campuri_lipsa(corp, ("valoare",), er=_er)
    _er.refuza()
    # ── I/O EXTERN, fără nicio conexiune în mână (termen 15 s) ──────────────────────────
    try:
        v = _ic.verifica_vies(_cod_client)
    except ValueError as e:
        raise _erori.DateInvalide(str(e))
    except Exception as e:
        _obs.esec_secundar("vies_verifica", e)   # [lotul 12, clasa 598] detaliul în jurnal, nu pe ecran
        raise _erori.ServiciuStrainCazut("Serviciul VIES al Comisiei Europene nu răspunde acum, deci codul de TVA nu s-a putut "
                                         "verifica. Încearcă din nou peste câteva minute.")
    # ── FAZA 2: tranzacție scurtă, cu REVALIDARE înainte de orice scriere ───────────────
    # Ce s-ar fi putut schimba în cele 15 s: accesul revocat, luna închisă de altcineva. Se cer
    # din nou, amândouă, iar la refuz iese exact eroarea de azi — rezultatul VIES se aruncă.
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
        _uc_comun._cere_luna_deschisa(conn, schema, corp.get("data"))
        try:
            # [R186/R187, 16.09.2026] TIPUL se valideaza contra nomenclatorului, nu se citeste cu
            # `== "servicii"`: axa se INGHEATA pe document, deci o valoare gresita ar ingheta o
            # minciuna. Pana azi orice altceva decat „servicii" devenea TACIT bunuri — aceeasi clasa
            # pe care lotul 5 a reparat-o la `achizitie_ic` pe 04.09. ([lotul 11, 440] verificat sus, cu codul și valoarea, înainte de VIES)
            # [C84, decizia Costin (b)] numai prestarea de servicii (bunurile s-au refuzat sus, înainte de VIES)
            if v.get("stare") == "indisponibil":   # [lotul 13, 550] VIES căzut nu e cod invalid: se reîncearcă, nu se taxează
                # 409 („reîncearcă”), ca la cursul BNR nepublicat: starea serviciului extern, nu o cădere a aplicației și nici a cererii
                raise _erori.Conflict(_ic.mesaj_vies_indisponibil(corp["cod_tva_client"], v.get("eroare")))
            ok, ment = _ic.valideaza_prestare_ic(corp["cod_tva_client"], v["valid"])
            cont_venit = _cv.cere_cont(conn, schema, corp.get("cont_venit"), "cont_venit", "704")
            cont_venit = _cv.cere_cont(conn, schema, cont_venit, "cont_venit")
            val = Decimal(str(corp["valoare"]))
            if val <= 0:
                # [R147] „valoare invalidă" nu spunea nici care valoare, nici ce se aștepta.
                raise ValueError("Valoarea operațiunii trebuie să fie un număr mai mare "
                                 "decât zero.")
        except (ValueError, KeyError) as e:
            raise _erori.DateInvalide(_uc_comun._mesaj_intrare(e))
        descr = (corp.get("descriere") or "Vânzare intracomunitară") + " - " + ment +                 f" [{v['nume']}]"
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
        # [lotul 12, C110] starea de plătitor a firmei, citită ca la celelalte emiteri (`facturi_emite`, API-ul, magazinul, recurentele),
        # nu implicitul „plătitor” al lui `emite_factura`: categoria liniei cu 0% se pune după ea (`categorii_tva.verifica_linii`)
        _platitor = _uc_comun._platitor_tva_firma(conn)
        try:   # [10.10.2026] refuzul motivat al emiterii ajunge la contabil (422), nu ca 500 (deficiența C7, generalizată)
            fres = _fa_vic.emite_factura(
                # [R193] contul de venit al liniei e cel ales mai sus (și pus pe notă), nu unul cerut modelului cu conexiunea ținută
                # [274b] bunurile: livrare intracomunitară scutită (K, D300 rd.1, D390 L); serviciile (art.278 alin.(2), locul prestării în
                # alt stat membru): „serviciu_extern” — D300 rd.3 + rd.3.1, D390 P (din axa facturii), AE + „taxare inversă” în XML și pe
                # PDF. [PIVOT 17.10.2026, decizia Costin pct.1] înlocuiește „în afara sferei TVA” din 16.10, respins.
                conn, linii=[{"descriere": descr[:200], "cantitate": 1, "pret_unitar": str(val),
                              "cota_tva": 0, "cont_venit": cont_venit,
                              "categorie_tva": "serviciu_extern"}],
                tert_nume=(v.get("nume") or "").strip() or None,
                tert_cui=corp["cod_tva_client"], data_emitere=corp["data"],
                tert_tara=_tara_client, axa_ic=corp.get("tip"), platitor_tva=_platitor)
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
        fid = fres["factura_id"]
        # [lotul 11, C78] Nota livrării e CONTAREA DE LA EMITERE (`facturi_api._conteaza_la_creare`: 4111 = contul de venit al liniei) — o
        # singură notă pe factură. Până azi se scria aici încă o notă 4111 = 707 pe aceeași factură: venitul și creanța ieșeau dublate, iar
        # a doua sumă nu se regăsea în niciun document (OMFP 2634/2015 anexa 1 pct.58 lit.c). Descrierea operațiunii (mențiunea scutirii,
        # numele din VIES) rămâne pe linia facturii. Contarea refuzată -> refuz numit, nimic scris (excepția întoarce toată tranzacția).
        _contare = fres.get("contare") or {}
        iid = _contare.get("inregistrare_id")
        if not iid:
            raise _erori.DateInvalide(
                "Livrarea intracomunitară nu s-a înregistrat: nota contabilă a facturii nu s-a putut scrie (%s). Nimic nu s-a scris."
                % ((_contare.get("afirmatie") or {}).get("motiv") or _contare.get("cod") or "contarea facturii lipsește"))
        conn.commit()
    # [lotul 12, C157] avertismentul emiterii (neplătitorul neînregistrat art.317): Operațiuni îl arată sub confirmare (`r.avertisment`)
    return _uc_comun.cu_eticheta(schema, {"inregistrare_id": iid, "factura_id": fid, "numar": fres.get("numar"),
            "mentiune": ment, "vies": v, "avertisment": " ".join(fres.get("avertismente") or []) or None})



def intrastat_praguri(tenant_id, an, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/intrastat-praguri`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an=an)
    from core import intrastat as _is
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
        raise _erori.EsecIntern("Șablonul pentru o firmă nouă lipsește pe server — anunță administratorul platformei.")
    # [comanda Costin 04.10.2026 pct.3] Emailul clientului se judecă ÎNAINTE de orice scriere. Până azi ecranul crea
    # firma și abia apoi trimitea adresa la `client-acces`: o adresă refuzată lăsa în urmă o firmă creată fără
    # portal, iar refuzul cădea într-un rând gri de sub CUI. Aceeași regulă ca la `client-acces` (o singură funcție).
    _email_cl = (getattr(date, "email_client", None) or "").strip().lower()
    # [440, comanda Costin 11.1 pct.16] denumirea, CUI-ul (cifra de control, `tenant_provisioning.cui_valid` — aceeași verificare ca la
    # creare) și emailul se judecă toate deodată (`ErorileFormularului`), fiecare lângă câmpul lui (ecranul: nume/cui/email_client ->
    # fn-nume/fn-cui/fn-email); CUI-ul / denumirea deja în portofoliu și adresa ocupată (starea evidenței) rămân refuzuri unice, după
    _er = _erori.ErorileFormularului("Firma nu s-a creat")
    if not tenant_provisioning.nume_normalizat(date.nume):
        _er.camp("nume", "Scrie denumirea firmei.")
    # [459] motivul vine din verificarea unică (`motiv_cui_firma_invalid`: numai cifre, fără 0 în față, 2–10 cifre, cifra de control)
    _m_cui = tenant_provisioning.motiv_cui_firma_invalid(date.cui)
    if _m_cui:
        _er.camp("cui", _m_cui)
    if _email_cl and not _uc_comun._email_valid(_email_cl):
        _er.camp("email_client", EMAIL_INVALID)
    if _er:
        raise _erori.CerereGresita(_er.detaliu())
    if _email_cl:
        with db.get_conn() as _c, _c.cursor(cursor_factory=_E_audit.RealDictCursor) as _cur:
            _uc_comun._refuza_email_ocupat(repo_utilizatori.contul_dupa_email(_cur, _email_cl), "client",
                                           _email_cl, "clientul firmei", "email_client")
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
            # [P5 val 3] datele ANAF s-au luat INAINTE de bloc (`_d_anaf`); aici doar scrie.
            # [lotul 12, 642 — clasa] precompletarea sub punct de revenire: o cădere nu mai anulează tăcut firma la commit
            tenant_provisioning.precompleteaza_sau_semnaleaza(conn, r["schema_name"], _d_anaf, "precompletare ANAF la firma noua")
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
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
    _crono.marca("acces")
    continut = continut
    _crono.marca("citire_fisier")
    try:
        tranzactii = banca_parser.parse_extras(continut, nume_fisier or "")
    except Exception as e:
        raise _erori.CerereGresita(f"nu s-a putut citi extrasul: {e}")
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



def spv_stare_firma(tenant_id, ctx):
    """[lotul 6] `spv_conector.stare_firma` pe firma cerută (principalul = cabinetul firmei)."""
    from core import spv_conector as _sc
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = repo_firma_profil.cui_firma(cur, schema)
        principal = _sc.principal_pentru_schema(conn, schema)
        if not principal:
            return {"conectat": False, "cui": "", "verificat_la": None, "are_drept": None, "eroare": None, "mesaje": None}
        return _sc.stare_firma(conn, principal, r[0] if r else "")


def spv_verifica_acum(tenant_id, ctx):
    """[lotul 6 pct.7b, 273] Citirea SPV a firmei, acum; întoarce rezultatul citirii + starea de după."""
    from core import spv_receive as _sr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    rez = _sr.citeste_firma(schema)
    return dict(citire=rez, stare=spv_stare_firma(tenant_id, ctx))


def facturi_primite_import_xml(tenant_id, fisiere, ctx):
    """[lotul 6 pct.7b, 273] `spv_receive.importa_xml_manual` pentru fiecare fișier încărcat."""
    from core import spv_receive as _sr
    schema = _uc_comun._schema_sau_404(ctx, tenant_id)
    tot = {"importate": 0, "deja": 0, "erori": []}
    for continut, nume in fisiere:
        r = _sr.importa_xml_manual(schema, continut, nume or "")
        tot["importate"] += r["importate"]; tot["deja"] += r["deja"]; tot["erori"] += r["erori"]
    return tot


def import_efactura(tenant_id, fisiere, ctx):
    """[P7 · use-case] Corpul rutei `/tenants/{tenant_id}/import-efactura`; docstringul ei a ramas in stratul HTTP."""
    from core import efactura_import as _ef
    rezultate = {"importate": 0, "duplicate": 0, "erori": []}
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
        if not schema:
            raise _erori.Inexistent("Firma nu există sau nu ai acces la ea.")
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
                    _alta = _ef.alta_firma(f, cui_firma)   # [clasa 599] factura între alte două firme nu intră
                    if _alta:
                        rezultate["erori"].append(f"{nume}: {_alta}")
                        continue
                    try:
                        _fid, _nou = _factura_importata(cur, schema, f)
                    except _chei.CheieDublata as e:   # [lotul 10, C73 / U2] numărul altei facturi emise: refuz numit pe fișier, nu 500
                        rezultate["erori"].append(f"{nume}: {e}")
                        continue
                    rezultate["importate" if _nou else "duplicate"] += 1
                    # [lotul 12, C161] ce nu s-a putut deduce sigur din XML-ul facturii emise (țara, felul operațiunii) se numește, nu se ghicește
                    rezultate.setdefault("avertismente", []).extend("%s: %s" % (nume, a) for a in f.get("avertismente") or [])
        conn.commit()
    return _uc_comun._raspuns(rezultate)

