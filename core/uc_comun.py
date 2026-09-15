# -*- coding: utf-8 -*-
"""USE_CASE — helperii comuni ai rutelor: acces, perioada, context, raspuns.

[P7 · valul use-case, 13.09.2026] Statele in `main.py`, deci in stratul HTTP, desi fac munca de
use-case: rezolva accesul la o firma (si isi deschid propria tranzactie pentru asta), refuza o
perioada care nu exista, traduc un refuz de intrare. **252 din cele 385 de rute** care isi detin
tranzactia foloseau cel putin unul — pana nu plecau ei, corpurile rutelor n-aveau unde sa se mute.

CE S-A PASTRAT, literă cu literă: corpul fiecarui helper, cu tot cu tranzactiile pe care le
deschide si cu ordinea efectelor. Ce s-a tradus: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o harta.
Se poate face fiindca **`HTTPException` nu e prinsa nicaieri** in aplicatie.

IN `main.py` a ramas, pentru fiecare, un INVELIS cu acelasi nume, care cheama versiunea de aici si
traduce refuzul inapoi. Asa rutele nemutate inca n-au vazut nicio diferenta — valul se face pe
loturi, si fiecare lot trebuie sa fie verde singur.
"""

import os
from core import cache_declarat as _cache_declarat
from core import cronometru as _crono
from core import db, auth_api, anaf_api, firma_profil_api as _fp
from core import repo_main as _repo
from core import stare_partajata as _stare_part
from core.mesaje import EMAIL_EXISTA, PERIOADA_INCHISA, MESAJ_CLIENT_ALT_CABINET, DOAR_ADMIN_CABINET, FARA_ACCES_TENANT
from fastapi.encoders import jsonable_encoder as _jsonable_encoder
from fastapi.responses import JSONResponse as _JSONResponse
import core.notificari_api as _notif
from core import erori as _erori
from core import afirmatii as _af
from core.mesaje import (EMAIL_EXISTA,
                         EMAIL_NICIUNUL_VALID, EMAIL_INVALID_LISTA, MESAJ_Z_DUPLICAT)
from core import db, auth_api, anaf_api, firma_profil_api as _fp, observare as _obs
import json as _json_audit
import logging as _logging
from core import raport_z as _raport_z
from core import common as _common
from core.common import stare_din_nivel


def _cere_perioada(an=None, luna=None, exercitiu=None, camp_an="an"):
    """Refuza o perioada care nu exista, INAINTE de a cauta date pentru ea.

    [lotul 3, 04.09.2026] Masurat pe sase rute: `luna=13` pe `GET /jurnal` dadea `500`; pe
    `GET /balanta`, pe calea de API si pe `registru-inventar/propunere` dadea `200` cu rezultat
    gol; iar `GET /documente/balanta?luna=0` **genera un PDF** — un document oficial pentru o luna
    care nu exista. Cel mai rau era `balanta`, care adauga si o afirmatie: `"stare":
    "nimic_de_verificat"`. *„Nu exista date pentru luna asta" si „luna asta nu exista" nu sunt
    acelasi lucru, iar a doua nu se repara cautand mai bine.*"""
    if luna is not None and not (1 <= luna <= 12):
        raise _erori.DateInvalide("luna invalidă: %r (aștept 1-12)" % (luna,))
    if an is not None and not (1990 <= an <= 2100):
        raise _erori.DateInvalide("%s invalid: %r (aștept 1990-2100)" % (camp_an, an))
    if exercitiu is not None and not (1990 <= exercitiu <= 2100):
        raise _erori.DateInvalide("exercițiu invalid: %r (aștept 1990-2100)" % (exercitiu,))


def _mesaj_intrare(e):
    """Mesajul unui refuz de intrare, cand exceptia poate fi si `KeyError`.

    [lotul 3, 04.09.2026] `except (ValueError, KeyError) as e: HTTPException(422, str(e))` apare in
    37 de locuri, iar pe ramura `KeyError` `str(e)` e **numele campului intre ghilimele simple**:
    contabilul primea `{"detail": "'brut'"}`. Cod intern ca mesaj — aceeasi clasa scoasa din coada
    in lotul 1, gasita aici pe alta cale. Se traduce o data, in locul comun."""
    if isinstance(e, KeyError):
        return ("Lipsește câmpul `%s` din cererea trimisă. Operațiunea nu se poate consemna fără "
                "el." % (e.args[0] if e.args else "?"))
    return str(e)


def _login_blocat(email):
    with db.get_conn() as conn:
        return _stare_part.login_blocat(conn, email)


def _login_esec(email):
    with db.get_conn() as conn:
        _stare_part.login_esec(conn, email)


def _login_reset(email):
    with db.get_conn() as conn:
        _stare_part.login_reset(conn, email)


def _hash_tok(t):
    import hashlib
    return hashlib.sha256((t or "").encode("utf-8")).hexdigest()


def _pune_token(cur, tok, user_id, interval_sql):
    """Curata expiratele/folositele, apoi stocheaza DOAR hash-ul tokenului (nu clarul)."""
    _repo.delete_public(cur)
    _repo.insert_public_3(cur, user_id, interval_sql, _hash_tok, tok)


def _termeni_versiune(txt):
    """Versiunea = linia 3 din fisier (fara markdown bold). Stocata la acceptare ca dovada."""
    linii = txt.split("\n")
    return (linii[2].strip().strip("*").strip() if len(linii) > 2 else "necunoscuta")


def _raspuns(continut):
    """Răspunsul JSON, serializat AICI — adică pe firul handler-ului, nu pe buclă.

    **De ce nu `return {...}`.** FastAPI nu serializează în handler: trece rezultatul prin
    `jsonable_encoder` și `json.dumps` în învelișul `async` de după, deci **pe buclă**, oricât de
    sincron ar fi handler-ul. Pentru un răspuns mare asta e muncă de zeci de milisecunde pe care o
    așteaptă toate celelalte cereri. Măsurat la P5: 67,6 ms de `jsonable_encoder` + 7,2 ms de
    `json.dumps` pentru 5000 de tranzacții (998 KB), din care ieșeau 93,7 ms de coadă la o cerere
    fără nicio legătură. *Valul 1 mutase handler-ul; răspunsul rămăsese unde era.*

    **Octeții sunt aceiași.** Fără `response_model` — și `main.py` n-are niciunul —
    `serialize_response` face exact `jsonable_encoder` (`fastapi/routing.py:317`), iar
    `JSONResponse.render` exact `json.dumps` cu aceiași parametri (`starlette/responses.py:194`).
    Se schimbă firul pe care se produc, nu conținutul.

    **Se folosește numai unde răspunsul crește cu intrarea.** Pe un răspuns mic, hopul în plus
    n-ar cumpăra nimic, iar `return {...}` se citește mai bine.
    """
    _crono.marca("inainte_serializare")
    r = _JSONResponse(_jsonable_encoder(continut))
    # [P5, 10.09.2026] Antetele de cronometrare, DOAR când instrumentarea e pornită. În producție
    # `_crono.antete()` întoarce `{}`, deci răspunsul e octet cu octet cel dinainte — inclusiv
    # antetele. *O măsurătoare care schimbă lucrul măsurat nu măsoară nimic.*
    for _k, _v in _crono.antete().items():
        r.headers[_k] = _v
    return r


def _octetii(fisier):
    """Conținutul unui fișier încărcat, citit SINCRON — pentru rutele `def`.

    **De ce nu `await fisier.read()`.** `UploadFile.read()` e `async`, dar pe un fișier ținut în
    memorie face chiar `self.file.read()`, iar pe unul ajuns pe disc îl trece prin
    `run_in_threadpool` (`starlette/datastructures.py:462`). Într-un handler **sincron** suntem
    deja pe un fir din threadpool, deci hopul n-ar avea ce să elibereze — și `await` n-ar avea
    cine să-l aștepte. Parserul de multipart lasă fișierul poziționat la 0
    (`starlette/formparsers.py:266`), deci octeții sunt acaeiași.

    **Nu se «repară» înapoi în `await fisier.read()`.** Asta ar cere ca ruta să redevină
    `async def`, adică exact defectul măsurat la P5: 17 rute care țineau bucla de evenimente
    ocupată cât dura importul cuiva. Măsurat: la N=5000 de tranzacții, o cerere fără nicio
    legătură aștepta 158,7 ms, față de 3,4 ms linia de bază.
    """
    return fisier.file.read()


def _schema_sau_404(ctx, tenant_id):
    """Verifică accesul userului la tenant; întoarce schema sau ridică 404."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    return schema


def _anaf_tva_check(cui, valoare_manuala):
    """[F180] Live ANAF v9 pe CUI. Întoarce (anaf_val|None, avertisment|None, tva_data_inceput|None). NU atinge
    DB și NU ridică niciodată (ANAF jos/notFound -> (None,None,None), salvarea trece — signal-not-block).
    anaf_val None = ANAF necunoscut -> snapshot NU se reîmprospătează. [B1] data inceperii inregistrarii TVA."""
    try:
        c = (cui or "").replace("RO", "").strip()
        if not c:
            return None, None, None
        rez = anaf_api.valideaza_cui([c])
        if not (rez and rez[0].get("gasit")):
            return None, None, None
        anaf_val = bool(rez[0].get("platitor_tva"))
        return anaf_val, _fp.avertisment_tva_anaf(valoare_manuala, anaf_val), rez[0].get("tva_data_inceput")
    except Exception:
        return None, None, None


def _platitor_tva_firma(conn):
    """Citeste daca firma emitenta e platitoare TVA (din firma_profil)."""
    with conn.cursor() as cur:
        row = _repo.select_firma_profil_2(cur)
    return bool(row[0]) if row and row[0] is not None else True


def _moneda_facturii(schema, factura_id):
    """Moneda unei facturi, citita intr-o tranzactie SCURTA — ca pre-incalzirea cursului sa se
    poata face inainte de cea de emitere. [P5 val 3, 11.09.2026]"""
    with db.get_conn(schema) as _c:
        with _c.cursor() as _cur:
            _r = _repo.select_facturi(_cur, factura_id)
    return (_r[0] if _r else None)


def _notif_de_validat(conn, cabinet_id, tip, perioada, creat_de_id):
    # notifica validatorii (mai putin pregatitorul)
    ids = _notif.validatorii_cabinetului(conn, cabinet_id, exclude_id=creat_de_id)
    txt = "Declaratie %s (%s) trimisa spre validare." % ((tip or "").upper(), perioada or "")
    _notif.adauga_multi(conn, ids, "de_validat", txt, link="validat")


def _pachet_schema(ctx, tenant_id):
    with db.get_conn() as c:
        schema = auth_api.schema_tenant(c, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent(FARA_ACCES_TENANT)
    return schema


def _email_client_tenant(conn, tenant_id):
    with conn.cursor() as cur:
        r = _repo.select_public_6(cur, tenant_id)
    return r[0] if r else None


def _nume_tenant(conn, tenant_id):
    with conn.cursor() as cur:
        r = _repo.select_public_7(cur, tenant_id)
    return r[0] if r else ""


def _tenant_client(ctx, tenant_id=None):
    """Rezolvă tenantul clientului din user_tenants. Un singur tenant -> implicit."""
    with db.get_conn() as conn:
        tenants = auth_api.tenantii_userului(conn, ctx["uid"])
    if not tenants:
        raise _erori.Inexistent("nu aveți nicio firmă asociată")
    if tenant_id is not None:
        t = next((x for x in tenants if x["id"] == tenant_id), None)
        if not t:
            raise _erori.Inexistent("firmă inexistentă sau fără acces")
        return t
    if len(tenants) == 1:
        return tenants[0]
    raise _erori.CerereGresita("Aveți mai multe firme; alegeți firma.")


def _titular_client(cur, tenant_id):
    """[R62 (b), 26.08.2026] Cine e titularul contului de portal: PRIMUL cont de client al firmei.

    Regula era scrisa in DOUA locuri si era DIFERITA. Citirea (`GET /portal/acces-cont`) cadea pe
    primul cont cand `tenants.principal_client_id` era NULL; cele trei scrieri comparau direct cu
    coloana. Cum coloana n-avea NICIO cale de scriere — zero INSERT, zero UPDATE, niciun ecran,
    iar `tenant_provisioning` insereaza fara ea — ecranul ii spunea omului *„esti titularul"* si ii
    arata butoanele, iar rutele ii raspundeau 403. **O afirmatie falsa pe ecran, la un om real**
    (utilizatorul #8284, firma #8396). Costin a ridicat-o la PRAG 1: *„ecranul spune una, serverul
    face alta"* — P13, in forma cea mai directa.

    Decizia lui, varianta (b): intrebarea se pune ALTFEL — primul cont de client — fiindca aia e
    regula pe care citirea o folosea deja. *„Alinierea lor nu adauga nimic — scoate o
    inconsistenta."* Iar *titular = primul venit* e o decizie de produs, asumata: la o firma mica,
    primul care primeste acces la portal e patronul sau administratorul. Daca se dovedeste gresita,
    se repara printr-o CALE de schimbare a titularului — alta functionalitate, nu o coloana.

    De aceea `principal_client_id` s-a si SCOS: o coloana cu drum de citire si fara drum de scriere
    e a treia cale prin care intrebarea s-ar putea pune altfel maine."""
    r = _repo.select_public_8(cur, tenant_id)
    if not r:
        return None
    return r["id"] if isinstance(r, dict) else r[0]


def _adresa_e_libera(cur, email, exclude_user_id):
    """[R62] Adresa nu e a altcuiva. UN singur loc, chemat si la cerere, si la confirmare.

    Intre cele doua momente pot trece 48 de ore: daca intrebarea ar fi pusa doar la cerere, o
    adresa luata intre timp ar fi aplicata peste, iar unicitatea s-ar sparge. Un loc, ca gardul
    sa poata asertea STRUCTURAL ca amandoua rutele il cheama."""
    if _repo.select_public_9(cur, email, exclude_user_id):
        raise _erori.CerereGresita(EMAIL_EXISTA)


def _urma_portal(cur, tenant_id, actiune, detaliu, autor_id):
    """[R62 (3), 26.08.2026] Urma pe care o vede CABINETUL.

    Pana azi, un client putea sa-si schimbe adresa de autentificare si sa creeze un utilizator
    SUB cabinet, fara ca acesta sa afle: niciun rand de audit, nicio notificare. Singurul email
    pleca la cel invitat. Append-only, `actiune` dintr-o lista inchisa in BAZA, `detaliu` care nu
    poate fi gol — o urma care nu spune nimic nu e o urma."""
    _repo.insert_public_4(cur, tenant_id, actiune, detaliu, autor_id)


def _cere_acelasi_cabinet(ex, firm_id):
    """[R62 (2), 26.08.2026] Un cont de client DEZACTIVAT al altui cabinet nu se reactiveaza aici.

    Ruta refuza deja o adresa care apartine unui cont ACTIV, sau unuia care nu e `client`. Dar un
    cont de client dezactivat intra pe ramura de reactivare si se lega de firma pastrandu-si
    `accounting_firm_id`-ul vechi — care poate fi al altui cabinet. Rezultatul: un utilizator care
    apartine, dupa coloana, cabinetului A, avand acces la o firma a cabinetului B.

    Costin a cerut punctul asta PRIMUL din cele trei: *„e singura cale prin care date ale unui
    cabinet ajung la altul, iar aia nu e o chestiune de urma, e izolarea din P12."*"""
    if not ex:
        return
    al_lui = ex.get("accounting_firm_id") if isinstance(ex, dict) else None
    if al_lui is not None and firm_id is not None and al_lui != firm_id:
        raise _erori.CerereGresita(MESAJ_CLIENT_ALT_CABINET)


def _perioada_blocata(conn, schema, data_nota):
    """True daca luna notei e blocata. data_nota: date sau str ISO.

    [29.08.2026] Interogarea s-a mutat in `core/contare_facturi.luna_blocata`, fiindca de azi o
    cere si contarea automata. Doua definitii ale lui „luna e blocata" ar fi dat doua raspunsuri la
    prima divergenta (P1); aici a ramas doar apelul."""
    from core import contare_facturi as _cf
    with conn.cursor() as cur:
        return _cf.luna_blocata(cur, schema, data_nota)


def _cere_luna_deschisa(conn, schema, data):
    """[R42 (a), 25.08.2026] P15 pe o notă NOUĂ, nu doar pe una existentă.

    Decizia lui Costin: *„o notă contabilă nu e ceva emis — e o înregistrare în evidență, nu un
    artefact predat. Dar nu e nici liberă: o notă care a intrat în evidență nu se șterge, se
    stornează."* Deci nu `admin_firma`, ci verificarea de perioadă.

    `_cere_perioada_deschisa` de mai jos păzea editarea, ștergerea și validarea unei note care
    EXISTĂ. Crearea intra pe altă ușă și nu era păzită: o notă nouă datată într-o lună închisă e
    tot o modificare a perioadei închise.

    [R146, 05.09.2026] O DATĂ LIPSĂ NU MAI TRECE TĂCUT. Până azi linia era `if not data: return` —
    adică „nu știu în ce perioadă suntem" se rotunjea la „e în regulă". Consecința nu era teoretică:
    **19 rute** ajungeau apoi la `INSERT ... VALUES (corp["data"], …)` și cădeau cu `KeyError` →
    **`500`**. Contabilul citea „eroare 500" în loc să afle că lipsește data.

    Dar motivul adevărat e mai adânc decât cele 19 căderi, și e o decizie de arhitectură a lui
    Costin (05.09.2026): *„cota de TVA se validează față de perioada în care cota a fost în vigoare,
    nu față de o listă de cote acceptate. Data operațiunii decide ce cote sunt legale. Aceeași
    regulă pentru praguri și plafoane."* Dacă data decide ce e legal, **o operațiune fără dată nu
    poate fi verificată de nimic** — nici cota, nici plafonul, nici perioada închisă. Absența ei nu e
    o lipsă de informație secundară: e imposibilitatea de a ști dacă înregistrarea e legală.

    Din cele 41 de locuri care cheamă poarta asta, **35** îi dau `corp.get("data")` — un câmp pe care
    ruta îl cere oricum mai jos; celelalte 6 îi dau o dată deja stabilită."""
    if not data:
        raise _erori.DateInvalide("Data operațiunii e obligatorie: de ea depind cota de TVA "
                                 "aplicabilă, plafoanele în vigoare și perioada contabilă. "
                                 "Fără ea, înregistrarea nu se poate verifica.")
    # [31.08.2026] Data se VALIDEAZĂ înainte de a fi întrebată despre perioadă. Fără asta,
    # `_perioada_blocata` primea „10.03.2025" brut, driverul de bază ridica, iar cererea ieșea 500 —
    # o defecțiune în locul unui refuz, exact înainte ca producătorul (care are refuzul scris, cu
    # temei) să apuce să fie chemat. Poarta de perioadă era corectă; ordinea nu era.
    from core import jurnal_api as _ja
    _d, _refuz = _ja._data_valida(data)
    if _refuz:
        raise _erori.CerereGresita({"mesaj": _refuz["eroare"], "temei": _refuz.get("temei"),
                                  "erori_campuri": [{"camp": "data", "mesaj": _refuz["eroare"]}]})
    if _perioada_blocata(conn, schema, _d):
        raise _erori.Blocat(PERIOADA_INCHISA)


def _cere_admin_firma(ctx, mesaj):
    """Verificarea pe care o face `cere_rol("admin_firma")`, dar în corp — pentru cazurile în care
    rolul cerut depinde de STAREA datelor, nu de rută. Aceeași comparație, ca să nu existe două
    definiții ale lui «e administrator» (P1)."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept(mesaj)


def _declaratie_generata(conn, tenant_id, tip, an, luna):
    """[R42 (b)] Există deja o declarație generată pentru perioada asta — în coadă sau depusă?

    Decizia lui Costin: *„o completare manuală e parte din declarație DA, după generare; NU,
    înainte. Înainte de generare e pregătire — se poate schimba fără consecință. După, declarația
    existentă nu mai corespunde datelor din care a ieșit."* Asta e P4 citit invers: documentul
    emis e fapt, deci ce l-a produs nu mai poate dispărea în tăcere."""
    from core import scadente as _sc
    try:
        perioada = _sc.scadenta(tip, an, luna=luna)
    except Exception:
        perioada = None
    with conn.cursor() as cur:
        if perioada:
            if _repo.select_public_10(cur, tenant_id, tip, perioada):
                return True
        return _repo.select_public_11(cur, tenant_id, tip, an, luna) is not None


def _cere_perioada_deschisa(conn, schema, nota_id):
    with conn.cursor() as cur:
        r = _repo.select_inregistrari(cur, schema, nota_id)
    if r and _perioada_blocata(conn, schema, r[0]):
        raise _erori.Blocat(PERIOADA_INCHISA)


def _facturi_neincheiate_in_perioada(cur, schema, an, luna):
    """[PPP1, 29.08.2026] Câte FACTURI ale perioadei sunt încă într-o stare neîncheiată.

    Poarta vedea, din 26.08, doar notele. O factură lăsată în `ciorna` sau în `de_recunoscut` e
    aceeași pierdere, pe alt obiect: documentul e acolo, dar actul care-l duce în evidență n-a fost
    făcut, iar după închidere nu se mai poate face — `contabilizeaza` și `recunoaste` cer amândouă o
    lună deschisă. **`de_recunoscut` e chiar starea introdusă azi la R91**, deci clasa n-avea cum să
    fie acoperită de verificarea scrisă acum trei zile.

    Se numără pe `data_emitere`, ca și restul porții: luna documentului, nu ziua în care cineva se
    uită la el."""
    from datetime import date as _d
    sfarsit = _d(an + (luna == 12), (luna % 12) + 1, 1)
    return _repo.select_facturi_2(cur, schema, sfarsit, _d, an, luna)[0]


def _ciorne_in_perioada(cur, schema, an, luna):
    """Câte note NEVALIDATE are perioada. [R58] O ciornă închisă înăuntru nu se mai poate valida,
    nu se mai poate șterge, și nu apare nicăieri — Costin: *„e o cheltuială sau un venit care
    dispare fără urmă."*"""
    from datetime import date as _d
    sfarsit = _d(an + (luna == 12), (luna % 12) + 1, 1)
    return _repo.select_inregistrari_2(cur, schema, sfarsit, _d, an, luna)[0]


def _schema_cabinet_sau_404(ctx, tenant_id):
    """Rezolva schema tenantului (conexiune separata); d390.pull foloseste nume necalificate,
    deci apelantul deschide apoi db.get_conn(schema) pozitionat pe schema."""
    with db.get_conn() as conn:
        schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    return schema


def _mesaj_scurt_inventar(e):
    """Pe camp incape o propozitie, nu o norma. Cauza e singura care are nevoie de mai mult de
    „cerut de norma": omul trebuie sa stie CA exista o diferenta, nu doar ca lipseste un camp."""
    if e.camp == "cauza":
        return "există o diferență între valoarea contabilă și cea de inventar — scrie cauza ei"
    if e.camp == "valoare_inventar":
        return "valoarea numărată; nu se completează singură din valoarea contabilă"
    return "cerut de normă, nu poate lipsi"


def _api_schema(actx, tenant_id):
    with db.get_conn() as conn, conn.cursor() as cur:
        r = _repo.select_public_12(cur, tenant_id, actx)
    if not r:
        # [probare invalid lot 2, 03.09.2026] Spunea „firmă inexistentă" și pentru o firmă care
        # EXISTĂ, dar e a altui cabinet — aceeași afirmație falsă scoasă din `FARA_ACCES_TENANT`
        # în lotul 1. Forma de acum nu deosebește cele două stări, deci nici nu divulgă care e.
        raise _erori.Inexistent("Firma nu există sau nu e în portofoliul cabinetului căruia îi "
                                 "aparține cheia de API folosită.")
    return r[0]


def _cer_admin_cabinet(ctx):
    """Doar admin_firma (și superadmin) gestionează actorii. Întoarce id cabinet."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept(DOAR_ADMIN_CABINET)
    return ctx["firm"]


def _are_permisiune(ctx, flag):
    """True dacă userul curent are flagul (poate_valida / poate_depune).
    superadmin trece mereu. Citește direct din public.users."""
    if ctx.get("rol") == "superadmin":
        return True
    if flag not in ("poate_pregati", "poate_valida", "poate_depune"):
        return False
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = _repo.select_public_13(cur, flag, ctx)
            return bool(r and r[0])


def _perioada_an(de, pana):
    """Fallback: daca lipsesc, perioada = anul curent (01.01 - 31.12)."""
    import datetime
    an = datetime.date.today().year
    return (de or f"{an}-01-01", pana or f"{an}-12-31")


def _rip_ctx(conn, ctx, tenant_id):
    schema = auth_api.schema_tenant(conn, ctx["uid"], tenant_id)
    if not schema:
        raise _erori.Inexistent("tenant inexistent sau fără acces")
    return schema


# ============================================================================================
# [P7 · valul use-case, lotul 2, 13.09.2026] Ultimii helperi si constantele de modul pe care 46
# de rute le cereau din `main.py`. Mutate VERBATIM; `HTTPException` tradus in `_erori`, cu acelasi
# mesaj. In `main.py` a ramas un invelis cu aceeasi semnatura pentru fiecare functie, iar
# constantele se importa inapoi de aici — o singura definitie, si acelasi OBIECT pentru cele
# mutabile (`_TENANT_TEMPLATE` se rescrie prin `pune_sablon_tenant`; `_magic_rate` a plecat la
# E1, in `public.cereri_ritm`, fiindca numararea trebuia sa fie una singura pe doua procese).
# ============================================================================================

BON_DIR_BAZA = "~/iconta_date/bonuri"


STARE_CIORNA = "ciorna"


_APP_PORNIT_LA = __import__("time").time()


_APP_URL = "https://iconta.eu"


_EVENIMENTE_PUBLICE = frozenset((
    "vizita_landing", "modal_functionalitati", "deschide_preturi", "intra_in_cont", "vizita_ghid"))


_LOG_VERDICT = _logging.getLogger("iconta.verdict")


_SURSE_Z = _raport_z.SURSE


_email_valid = _common.email_valid



def _acces_pentru_activare(conn, rol, firm, tenant_id):
    """[R83/JJ1, 28.08.2026] Poarta rutei de ACTIVARE — scrisă **local**, nu în funcția comună.

    DE CE EXISTĂ. `auth_api.schema_tenant` cere `activ = true` pe **toate trei** ramurile de rol.
    E corect pentru orice rută care lucrează *în* firmă — o firmă scoasă din portofoliul de lucru
    n-are de ce să răspundă la cereri de conținut. Dar ruta de activare e **singura** al cărei act
    are sens tocmai pe o firmă **inactivă**: reactivarea. Cu poarta comună, ea răspundea 404
    întotdeauna, deci **reactivarea nu se putea face niciodată** (R83, probat pe 28.08.2026).

    DE CE AICI ȘI NU ÎN `schema_tenant`. Decizia lui Costin — varianta **(a)**: *„restul rutelor
    rămân neatinse — nicio semnătură comună nu se schimbă, izolarea rămâne exact cum era."*
    Un parametru `si_inactive=` pe funcția comună ar fi reparat clasa, dar ar fi atins o semnătură
    folosită în **154** de rute, fiecare cu propriul risc *(numărate pe AST înainte de reparație;
    după ea sunt 153 — ruta asta a ieșit din mulțime)*. Excepția e locală, deci și riscul e.

    CE PĂSTREAZĂ NEATINS: **regula de rol**, identică cu a funcției comune —
      * `superadmin` ajunge doar la firme **fără cabinet** (GDPR: nu vede conținutul clienților);
      * oricine altcineva ajunge doar la firmele **cabinetului lui**.
    Singura diferență față de `schema_tenant` e `activ`, și e diferența cerută.

    CE NU FACE: nu întoarce schema și nu dă acces la **conținut**. Întoarce un `bool` — dreptul de a
    comuta un rând din `public.tenants`. Cine vrea conținutul firmei trece tot prin poarta comună.

    Refuzul e **același mesaj** ca al porții comune, deliberat: „inexistent" și „fără acces" nu se
    despart, ca să nu se poată afla din afară ce firme există.
    """
    with conn.cursor() as cur:
        r = _repo.select_public_3(cur, tenant_id)
    if not r:
        return False
    cabinet = r[0]
    if rol == "superadmin":
        return cabinet is None
    return cabinet is not None and cabinet == firm


def _flag_constatare(stare, eticheta, mesaj, temei, an, luna, remediu=None):
    # [verdict_colapsat] constatare STRUCTURATA (dot + mesaj + temei + remediu), randata identic cu D390/TVA
    # in control.js. `eticheta` = label scurt (sumar de lista + dedup fata de «Declaratie vs contabilitate»).
    # [P8, 21.08.2026] Constatarea E o afirmatie, imbracata pentru ecran - ca in control_incrucisat.
    # Felul se alege dupa STARE, fiindca asta E ce afirma: verde = am verificat si tine (fapt);
    # rosu = doua surse nu pot fi amandoua adevarate (contradictie); gri = nu pot spune (necunoastere).

    _txt = mesaj or eticheta
    if stare == "gri":
        _dom = ("%04d-%02d" % (an, luna)) if (an and luna) else (str(an) if an else None)
        _a = _af.afirmatie("necunoastere", eticheta, _txt, domeniu_de=_dom, domeniu_pana=_dom)
    elif stare == "rosu":
        _a = _af.afirmatie("contradictie", eticheta, _txt,
                           sursele="evidența contabilă a firmei; verificarea „%s”" % eticheta)
    else:
        _a = _af.afirmatie("fapt", eticheta, _txt, an=an, luna=luna,
                           temei_completitudine=temei or "verificarea „%s” a rulat pe datele lunii"
                                                         % eticheta)
    # Campurile se pun UNUL CATE UNUL: un `{... "mesaj": ...}` aici ar fi numarat de
    # `core/scan_afirmatii` drept inca o afirmatie netipata, iar CONSTRUCTORUL afirmatiilor ar aparea
    # pe vecie in clichet ca datorie. Nu e cosmetica - chiar exista un singur dictionar, imbogatit.
    _a["stare"] = stare
    _a["eticheta"] = eticheta
    _a["mesaj"] = _txt
    _a["temei"] = temei or ""
    _a["remediu"] = remediu
    return _a


def _constatare_esuata(eticheta, nume, e, an, luna):
    """Constatare GRI pentru un verificator care CRAPA (nu 'nimic de raportat' - e 'nu am putut verifica').
    Excepția înghițită face firma să pară mai curată decât e (minciună prin omisiune). GRI nu escaladeaza
    pastila_firma (rezistenta se pastreaza - un esec izolat nu doboara semaforul), dar il anunta pe CONTABIL,
    care decide. Doua straturi: GRI = principal (il vede contabilul); log = secundar (sa se vada daca pica
    SISTEMATIC). Vezi DECIZII 23.07. Intoarce constatarea (apelantul o pune unde e vizibila)."""
    _LOG_VERDICT.warning("verificator esuat pe cale de verdict: %s -> gri (%r)", nume, e)
    return _flag_constatare("gri", eticheta, "Nu am putut verifica %s." % nume,
        "Verificarea a eșuat (%s). GRI înseamnă 'nu am putut verifica', NU 'curat' — o constatare reală "
        "poate lipsi. Reîncarcă; dacă persistă, semnalează." % e, an, luna)


def _preincalzeste_cursul(moneda, data_emitere):
    """[P5 val 3, 11.09.2026] Aduce cursul BNR ÎNAINTE de orice tranzacție.

    `curs_bnr.curs_pentru` nu mai descarcă: decide pe cache. Descărcarea (până la 3×10 s) trebuie
    deci să se fi făcut înainte, cu pool-ul liber. Un singur loc, ca să nu ajungă șapte rute să
    repete aceeași secvență — și ca garda să aibă ce număra.

    Tăcută la intrări invalide: refuzul lor vine de la validarea rutei, ca și până acum.
    """
    from datetime import date as _d
    from core import uc_curs_bnr as _uc_cb
    if not moneda or str(moneda).upper() == "RON" or not data_emitere:
        return
    try:
        zi = data_emitere if isinstance(data_emitere, _d) else _d.fromisoformat(str(data_emitere))
        _uc_cb.asigura_cursul(str(moneda), zi)
    except Exception:      # noqa: BLE001 — pre-încălzirea nu poate strica o cerere
        pass


def _coada_info(conn, coada_id):
    with conn.cursor() as cur:
        r = _repo.select_public_5(cur, coada_id)
    if not r:
        return None
    return {"tip": r[0], "perioada": r[1], "creat_de_id": r[2], "cabinet_id": r[3]}


def _notif_pregatitor(conn, coada_id, tip_eveniment, motiv=None):
    info = _coada_info(conn, coada_id)
    if not info or not info["creat_de_id"]:
        return
    tip = (info["tip"] or "").upper()
    per = info["perioada"] or ""
    if tip_eveniment == "respinsa":
        txt = "Declaratia %s (%s) a fost respinsa." % (tip, per)
        if motiv:
            txt += " Motiv: " + motiv
    elif tip_eveniment == "aprobata":
        txt = "Declaratia %s (%s) a fost aprobata." % (tip, per)
    elif tip_eveniment == "depusa":
        txt = "Declaratia %s (%s) a fost depusa." % (tip, per)
    else:
        txt = "Actualizare declaratie %s (%s)." % (tip, per)
    _notif.adauga(conn, info["creat_de_id"], tip_eveniment, txt, link="validat")


def _interval_cerut(valoare, nume, minim, maxim, unitate):
    """[R150, 05.09.2026] O valoare in afara intervalului se REFUZA, cu numele campului si limitele.

    Pana azi cele trei rute de mai jos faceau `min(max(v, jos), sus)` — adica inlocuiau tacut o
    valoare imposibila cu una convenabila. Masurat, apasand: `?ore=-5` intorcea `200` cu istoricul
    ultimei ore, iar `?ore=99999` intorcea 168 de ore. Omul care a cerut 99999 crede ca se uita la
    99999. *O coercitie tacita nu e o protectie, e o afirmatie falsa despre ce s-a cerut.*

    `admin_analytics` era cazul cel mai bland — el ISI ECHIVALA valoarea folosita in raspuns
    (`{"zile": 1}`), deci se putea vedea. Celelalte doua, nu. Se trateaza la fel toate trei: o
    intrare imposibila primeste un refuz care spune intervalul.
    """
    try:
        v = int(valoare)
    except (TypeError, ValueError):
        raise _erori.DateInvalide("%s trebuie să fie un număr întreg de %s. Am primit %r."
                            % (nume, unitate, valoare))
    if v < minim or v > maxim:
        raise _erori.DateInvalide("%s se cere între %d și %d %s. Am primit %d."
                            % (nume, minim, maxim, unitate, v))
    return v


def _cere_z_unic(cur, schema, numar):
    """[R61, 26.08.2026] Un raport Z e unic pe casa de marcat si pe zi — deci pe NUI + numar.

    Decizia lui Costin: *„raportul Z e un document al casei de marcat, unic pe zi si pe aparat.
    Doua rapoarte Z pe aceeasi data nu exista in realitate, deci nici in evidenta."* Varianta (a)
    din R61: a doua nota se REFUZA, nu se accepta cu stornare — un duplicat nu e o corectie, e o
    greseala de operare.

    Cauta in AMANDOUA sursele. Cheia e aceeasi la ruta tastata si la import, deci un raport deja
    importat nu mai poate fi tastat a doua oara, si invers — altfel poarta ar fi tinut doar
    jumatate din drum."""
    r = _repo.select_2(cur, schema, numar, _SURSE_Z)
    if not r:
        return
    iid, data_ex, sursa = (r["id"], r["data"], r["sursa"]) if isinstance(r, dict) else r
    raise _erori.Conflict(MESAJ_Z_DUPLICAT % {
        "numar": numar, "data": data_ex, "id": iid,
        "cum": "importata din fisier AMEF" if sursa == "amef" else "tastata"})


def _cere_an_luna(corp):
    """(an, luna) din corp, sau 422. Nu KeyError -> 500: o cerere incompleta e o cerere gresita, nu
    o defectiune a serverului, iar 500 spune mai mult decat trebuie despre ruta."""
    try:
        an, luna = int((corp or {})["an"]), int((corp or {})["luna"])
    except (KeyError, TypeError, ValueError):
        raise _erori.DateInvalide("lipsesc an și luna")
    if not (1 <= luna <= 12):
        raise _erori.DateInvalide("luna trebuie să fie între 1 și 12")
    return an, luna


def _verifica_documente_pozate(schema):  # verif_doc_pozate_v1
    """Documente pozate de clienti blocate in flux: necontate >3 zile sau note ciorna casa >3 zile."""
    with db.get_conn() as conn, conn.cursor() as cur:
        bonuri_vechi = _repo.select_bonuri(cur, schema)[0]
        ciorne = _repo.select_casa_operatiuni(cur, schema)[0]
    return {"ok": bonuri_vechi == 0 and ciorne == 0,
            "bonuri_neverificate": bonuri_vechi, "ciorne_casa": ciorne}


def _verificari_contabile(schema, an, luna):
    from core import verificatoare as _vf
    from datetime import date as _date
    sfarsit = _date(an + (luna == 12), (luna % 12) + 1, 1)
    with db.get_conn() as conn, conn.cursor() as cur:
        note = [{"debit": r[0], "credit": r[1], "suma": r[2]} for r in _repo.select_inregistrari_linii(cur, schema, sfarsit)]
        si = {r[0]: r[1] for r in _repo.select_solduri_initiale(cur, schema)}
    bal = _vf.balanta(note, si)
    # [R33 varianta b'', 26.08.2026] ECHILIBRUL E UN VERDICT COMPUS DIN DOUA VERIFICARI.
    # Pana azi aici rula doar `verifica_balanta`, iar `core/echilibru_perioada` -- scris, testat,
    # cu garda proprie -- nu era chemat de nimeni. Se credea ca e "a doua implementare a aceleiasi
    # verificari"; masurat pe aceleasi date (25.08.2026), modurile de esec sunt DISJUNCTE:
    #   echilibru_perioada -> linia cu o parte lipsa (NULL, gol sau numai spatii) si orfanul;
    #   verifica_balanta   -> soldurile initiale care nu se inchid.
    # Fiecare o rateaza pe cealalta, deci a alege una ar fi STERS o verificare (CONFORMITATE R33).
    # Cele doua se compun intr-un SINGUR verdict `echilibru` -- contabilul nu trebuie sa stie ca
    # sunt doua module -- iar compunerea se face LA CONSTRUCTIE, in verdict_echilibru (pur).
    # LIMITA DECLARATA: felia de ledger e LUNA curenta si doar notele `validata` (domeniul
    # modulului); o ciorna cu contul rupt se vede abia dupa validare, cand devine evidenta.
    from core import echilibru_perioada as _ep
    try:
        with db.get_conn() as _cl:
            _ledger = _ep.echilibru_perioada_db(_cl, schema, an, luna)
    except Exception as _e:
        # verificare RUPTA, nu date curate: verdict_echilibru o trece la `neverificat`, deci
        # verdele nu se poate afirma peste ea (P6).
        _ledger = {"eroare": "%s: %s" % (type(_e).__name__, _e)}
    # [control_incrucisat_v1 + F163_ui] punti declaratie <-> contabilitate/evidenta (D-vs-contabilitate):
    #   D300 vs 4427/4426 · D112 (salarii) vs 444/4315/4316/436 · D390 (bunuri IC) vs evidenta validata.
    # Motoare SEPARATE (core/control_incrucisat), doar EXPUSE aici - aceeasi anatomie (trei stari + temei +
    # remediu). NU se atinge engine-ul. Fiecare pe conexiune proprie pe schema; esec izolat -> gri cu cauza
    # (gri e informatie, nu absenta - filozofia control_incrucisat), nu doboara ceilalti verificatori.
    from core import control_incrucisat as _ci
    def _incrucisat(fn, eticheta):
        try:
            with db.get_conn(schema) as _c:
                return fn(_c, schema, an, luna)
        except Exception as _e:
            # [P8] VERIFICARE RUPTA: motorul a crapat, nu datele lipsesc. Pe ecran ramane gri, in
            # date se DEOSEBESTE - cine numara „cate nu pot fi verificate" nu mai inghite si rupturile.
            # Starea intra la CONSTRUCTIE, nu prin atribuire dupa: `_c["stare"] = "gri"` e prins de
            # verificator (VERDICT_COLAPSAT, stare-literal), si pe drept - un verdict carpit dupa
            # constructie are doua surse. A doua oara azi cand fac asta.
            _c = dict(_af.afirmatie("verificare_rupta", eticheta,
                                    "NU pot verifica %s: %s" % (eticheta, _e),
                                    eroare="%s: %s" % (type(_e).__name__, _e)),
                      stare="gri", eticheta=eticheta, temei="Verificarea nu a rulat.",
                      remediu={"fel": "investigatie", "cauza": "Eroare la verificare.",
                               "actiune": "Reîncearcă; dacă persistă, verifică datele firmei.",
                               "facturi": []})
            _c["mesaj"] = _c["motiv"]
            return {"stare": "gri", "constatari": [_c],
                    "limita": "Verificarea %s nu a rulat: %s" % (eticheta, _e)}
    tva_incr = _incrucisat(_ci.verifica_tva, "TVA")
    d112_incr = _incrucisat(_ci.verifica_d112, "salarii (D112)")
    d390_incr = _incrucisat(_ci.verifica_d390, "operatiuni intracomunitare (D390)")
    # [F184] conformitate cota TVA facturi emise vs cota standard pe perioada (value-aware, NU decl-vs-contab)
    cota_tva_incr = _incrucisat(_ci.verifica_cota_tva, "cotă TVA facturi emise")
    rezultat = {
        "tva_incrucisat": tva_incr,
        "d112_incrucisat": d112_incr,
        "d390_incrucisat": d390_incr,
        "cota_tva_conformitate": cota_tva_incr,
        "echilibru": _ep.verdict_echilibru(_ledger, _vf.verifica_balanta(bal),
                                           "%04d-%02d" % (an, luna)),
        "trezorerie": _vf.verifica_trezorerie(bal),
        "tva": _vf.coerenta_tva(bal.get("4427", {}).get("credit", 0), bal.get("4426", {}).get("debit", 0)),
        "note": len(note),
    }
    try:  # verif_doc_pozate_v1
        rezultat["documente_pozate"] = _verifica_documente_pozate(schema)
    except Exception as e:
        # gri, nu tacere: chiar daca azi nu e surfacat in pastila, devine corect cand cineva il surfaceaza.
        rezultat["documente_pozate"] = _constatare_esuata("Documente pozate — verificare eșuată", "documentele pozate", e, an, luna)
    # [d205_legacy_eliminat 23.07] Verificarea d205_vs_457 a fost ELIMINATA: citea suma D205 din tabela
    # d205_beneficiari care NU are niciun writer in cod -> suma_d205 era mereu 0 -> orice firma cu dividende
    # (1171->457) primea rosu fals. D205 real foloseste cont 457 din d205.py; coerenta D205-vs-457 pe FAPT
    # traieste deja in semafor (control_incrucisat.dividende_distribuite via declaratii_fapt). Vezi DECIZII 23.07.
    return rezultat


def _tenant_pentru_documente(ctx, tenant_id):  # bon_cabinet_v1
    """Client -> firma lui (ca pana acum); rolurile de cabinet -> tenant_id obligatoriu,
    cu verificarea accesului. Intoarce dict cu schema_name + id."""
    if (ctx.get("rol") or "") == "client":
        return _tenant_client(ctx, tenant_id)
    if not tenant_id:
        raise _erori.CerereGresita("Alegeți firma (necesar pentru rolurile de cabinet).")
    return {"schema_name": _schema_sau_404(ctx, tenant_id), "id": tenant_id}


def _bon_imagine_cale(schema, bon_id, n):
    import os as _os, glob as _glob
    cai = sorted(_glob.glob(_os.path.join(_os.path.expanduser(BON_DIR_BAZA), schema, str(int(bon_id)), "img_%d.*" % int(n))))
    return cai[0] if cai else None


def _trimite_recomandari(emails, html, subiect):
    if not emails:
        raise _erori.CerereGresita(EMAIL_NICIUNUL_VALID)
    if len(emails) > 20:
        raise _erori.CerereGresita("Maxim 20 de emailuri odata.")
    # [R154, 05.09.2026] Masurat apasand: `{"emails": ["«»@#$%"]}` intorcea
    # `200 {"stare": "esuat"}` — adica aplicatia SPUNEA ca n-a putut trimite, dupa ce chemase
    # furnizorul de email cu un sir care nu poate fi adresa nimanui. Constanta de deasupra se
    # cheama chiar `EMAIL_NICIUNUL_VALID`, deci verificarea era promisa in registrul de mesaje
    # si nu exista in cod. Criteriul e cel din R138 (`core.common.email_valid`), imprumutat, nu
    # rescris — a doua definitie a aceluiasi lucru e inceputul unei divergente tacute.
    #
    # REFUZUL E PE TOATA LISTA, nu pe adresele rele: o trimitere partiala ar fi lasat omul cu
    # „3 trimise” si fara sa stie ca a patra n-a plecat niciodata — aceeasi coercitie tacuta ca
    # la R150. Se refuza tot, si se spune CARE adresa nu e adresa.
    rele = [e for e in emails if not _email_valid(e)]
    if rele:
        raise _erori.DateInvalide(EMAIL_INVALID_LISTA % ", ".join(rele[:5]))
    rezultate = []
    for em in emails:
        ok = _obs.trimite_email_html(em, subiect, html)
        rezultate.append({"email": em, "stare": "trimis" if ok else "esuat"})
    return rezultate


def _mesaj_recomanda_client_html(nume_firma):
    return (
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:540px;line-height:1.55'>"
        "<p>Buna,</p>"
        "<p>Sunt client iConta.eu si ma tine departe de batai de cap cu ANAF - "
        "imi arata din timp daca am ceva de depus sau de platit, inainte sa fie o problema.</p>"
        "<p>M-am gandit ca ti-ar prinde bine si tie.</p>"
        "<p style='margin:24px 0'><a href='https://iconta.eu' style='background:#2563eb;color:#fff;"
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Vezi iConta.eu</a></p>"
        "</div>"
    )


def _mesaj_promo_html(nume_cabinet):
    # [p32_mesaj] text cu diacritice, 4 atribute principale ale aplicatiei
    cine = nume_cabinet or "Un cabinet de contabilitate"
    _li = "margin:0 0 10px 0;padding-left:2px"
    return (
        "<!-- [p32_mesaj] -->"
        "<div style='font-family:sans-serif;font-size:15px;color:#111;max-width:540px;line-height:1.55'>"
        "<p>Bună,</p>"
        "<p>" + cine + " folosește <b>iConta.eu</b> și s-a gândit că ți-ar prinde bine și ție.</p>"
        "<p>iConta.eu e contabilitatea în cloud care lucrează pentru tine și echipa ta:</p>"
        "<ul style='margin:14px 0;padding-left:20px'>"
        "<li style='" + _li + "'><b>Te apără</b> &mdash; semaforul fiscal te avertizează înainte "
        "să depui ceva ce-ți aduce control.</li>"
        "<li style='" + _li + "'><b>Face munca grea</b> &mdash; citește documentele și propune "
        "contările; tu doar verifici și aprobi.</li>"
        "<li style='" + _li + "'><b>Îți conduce echipa</b> &mdash; împarți firmele pe asistenți, "
        "urmărești cine ce lucrează, cu validare în patru ochi înainte de depunere.</li>"
        "<li style='" + _li + "'><b>Adună tot</b> &mdash; contabilitate, salarizare, declarații, "
        "e-Factura și SAF-T, pe același client.</li>"
        "</ul>"
        "<p>Mai puțin timp pierdut, mai puține greșeli costisitoare.</p>"
        "<p style='margin:24px 0'><a href='" + _APP_URL + "' style='background:#2563eb;color:#fff;"
        "padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:600'>Încearcă iConta.eu</a></p>"
        "</div>"
    )


def _jurnal_rez(rez):
    if rez is None:
        raise _erori.Inexistent("notă inexistentă")
    if rez.get("eroare"):
        # [31.08.2026] Refuzul poartă temeiul mai departe, pe contractul comun
        # `detail.erori_campuri`. Până azi îl turtea într-un șir: producătorul putea spune sub ce
        # normă refuză, iar ruta arunca partea aia. Interdicția 77 pe cea mai folosită cale de
        # scriere — măsurată în exercițiul de intrare din 31.08, 12 refuzuri fără niciun temei.
        if rez.get("temei"):
            # Producătorul întoarce o AFIRMAȚIE tipată (`neconformitate`); ruta o trece mai departe
            # întreagă, nu construiește un al doilea obiect din bucăți. Prima formă o reconstruia,
            # și era ea însăși o afirmație netipată — prinsă de gardul din 21.08.
            det = dict(rez)
            det["mesaj"] = rez["eroare"]
            if rez.get("camp"):
                det["erori_campuri"] = [{"camp": rez["camp"], "mesaj": rez["eroare"]}]
            raise _erori.CerereGresita(det)
        raise _erori.CerereGresita(rez["eroare"])
    return rez


def _urma_dezlegare(conn, uid, tenant_id, nota_id, factura_id, motiv):
    """URMA actului, ca FAPTĂ, nu doar ca linie de acces.

    Middleware-ul de audit scrie deja `POST <cale>` cu statusul, pentru orice mutație — dar atât:
    *că* s-a cerut ceva, nu *ce* s-a dezlegat. Aici se scrie fapta: care notă, de pe care factură,
    cu ce motiv. Se folosește ACELAȘI tabel (`public.audit_log`), cu aceeași sub-interogare pe
    `tenant_id` ca middleware-ul — R79: un rând de audit scris după o ștergere ar trimite la o firmă
    care nu mai există."""
    from core import afirmatii as _af
    # Urma e o AFIRMAȚIE TIPATĂ, nu proză într-un dicționar (P3, decizia din 21.08): `fel='fapt'`,
    # fiindcă exact asta e — un fapt petrecut, cu domeniul lui (nota și factura) și cu temeiul care
    # spune de ce e completă. Prima formă scria `{"motiv": ...}` și a fost prinsă de
    # `test_afirmatii_tipate`: o cheie de revendicare fără `fel` e chiar clasa vânată acolo.
    fapt = _af.afirmatie(
        "fapt", "DEZLEGARE_NOTA_FACTURA", motiv[:500],
        unde="nota #%s, factura #%s" % (nota_id, factura_id),
        temei_completitudine="urma se scrie în ACEEAȘI tranzacție cu dezlegarea, deci nu poate "
                             "exista dezlegare fără ea",
        nota_id=nota_id, factura_id=factura_id)
    with conn.cursor() as cur:
        _repo.insert_public_5(cur, uid, tenant_id, fapt, _json_audit)


def _factura_din_parsat(cur, schema, f):
    """Insereaza o factura parsata (dict de la efactura_import.parseaza_xml) in facturi + linii.
    Idempotent pe (numar, tert_cui, data_emitere). Intoarce (factura_id, creat_nou): daca exista
    deja, intoarce id-ul EXISTENT + False (nu insereaza). Sursa UNICA a inserarii - folosit de
    /import-efactura (upload manual) SI de validarea four-eyes a facturilor primite (nu doua conducte)."""
    ex = _repo.select_facturi_3(cur, schema, f)
    if ex:
        return ex[0], False
    # [R91/KKK1] Starea depinde de DIRECȚIE, și nu e o subtilitate:
    #   * **primită** -> `importata`, ca până acum. Recunoașterea ei există deja și e alt act:
    #     `/facturi-primite/{id}/valideaza`, unde omul alege contul și clasifică regimul (R88).
    #   * **emisă** -> `de_recunoscut`. Documentul a fost emis în altă parte, deci sosirea lui nu e
    #     faptul economic al firmei. Nota vine din `/facturi/{id}/recunoaste`.
    # **NICIUNA nu primește notă aici** — la fel ca înainte. Ce se schimbă e că absența nu mai e o
    # scăpare declarată, ci o etapă cu act propriu.
    _stare = "de_recunoscut" if f["directie"] == "emisa" else "importata"
    fid = _repo.insert_facturi(cur, schema, _stare, f)[0]
    for ln in f["linii"]:
        _repo.insert_factura_linii(cur, schema, fid, ln)
    return fid, True


# ============================================================================================
# [P7 · valul use-case, lotul 2] STAREA DE PORNIRE, pusa de stratul HTTP, consumata aici.
# Nu sunt constante: se afla la pornire, in `main.py` (una citita din fisier in `lifespan`, alta
# aleasa de `_alege_static()`, care tot acolo monteaza `/static`). Daca ar fi mutate ca valori,
# use-case-ul ar ramane cu `None`, iar scriitorul cu copia lui. Deci valoarea sta AICI si stratul
# HTTP o pune, la momentul in care o stie.
# ============================================================================================

#: sablonul de creare a unei firme; `None` pana e citit, iar crearea da atunci un refuz clar.
_TENANT_TEMPLATE = None
_TENANT_TEMPLATE_DECLARATIE = _cache_declarat.Declaratie(
    rol="sablonul SQL al schemei unui tenant nou, citit o data la pornire",
    sursa="fisierul de la `TENANT_TEMPLATE_PATH` (implicit `tenant_template.sql`, versionat)",
    motiv="citirea unui fisier SQL mare pe calea crearii unei firme",
    invalidare="la repornirea procesului. Identic pe orice numar de instante, fiindca toate "
               "pornesc din acelasi commit — deci nu poate diverge intre procese",
    dovada="core/test_cache_declarat.py::test_sablonul_de_tenant_se_reconstruieste_identic",
)

#: directorul din care se servesc fisierele statice — si in care se scriu capturile de raportari.
_STATIC_DIR = None
_STATIC_DIR_DECLARATIE = _cache_declarat.Declaratie(
    rol="directorul din care se servesc fisierele statice, ales o data la pornire",
    sursa="`main._alege_static()` — arborele publicat daca exista, altfel cel de lucru",
    motiv="alegerea se face cu apeluri de sistem de fisiere; refacuta la fiecare cerere, ar pune "
          "un `stat` pe calea fiecarei imagini servite",
    invalidare="la repornirea procesului. Identic pe orice numar de instante: alegerea depinde de "
               "commitul publicat si de disc, nu de cerere — deci nu poate diverge intre procese",
    dovada="core/test_cache_declarat.py::test_static_dir_e_pus_de_stratul_HTTP",
)

#: calea fisierului de termeni. Constanta, dar derivata din locul MODULULUI: radacina e cu un
#: nivel mai sus decat `core/`, si se scrie explicit ca sa nu depinda de cine importa.
_TERMENI_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "TERMENI_SI_CONDITII.md")


def pune_sablon_tenant(text):
    """Stratul HTTP a citit sablonul (sau n-a gasit fisierul, si atunci e `None`)."""
    global _TENANT_TEMPLATE
    _TENANT_TEMPLATE = text


def pune_static_dir(cale):
    """Stratul HTTP a ales directorul static; use-case-ul scrie capturile acolo."""
    global _STATIC_DIR
    _STATIC_DIR = cale


# ============================================================================================
# [P7 · valul use-case, lotul 2, 13.09.2026] Ultimii helperi si constantele de modul pe care 46
# de rute le cereau din `main.py`. Mutate VERBATIM; `HTTPException` tradus in `_erori`, cu acelasi
# mesaj. In `main.py` a ramas un invelis cu aceeasi semnatura pentru fiecare functie, iar
# constantele se importa inapoi de aici — o singura definitie, si acelasi OBIECT pentru cele
# mutabile (`_TENANT_TEMPLATE` se rescrie prin `pune_sablon_tenant`; `_magic_rate` a plecat la
# E1, in `public.cereri_ritm`, fiindca numararea trebuia sa fie una singura pe doua procese).
# ============================================================================================




def _verificator_esuat(contabil, eticheta, nume, e, an, luna):
    """Varianta pt lista de constatari (contabil): adauga constatarea gri. Vezi _constatare_esuata."""
    contabil.append(_constatare_esuata(eticheta, nume, e, an, luna))


def _construieste_contabil(schema, tid, ctx, an, luna, regim_tva_anaf):
    """Constatarile contabile STRUCTURATE ale unei firme + verificari_contabile brute (vc). UN SINGUR loc,
    folosit de LISTA (portofoliu) SI de DETALIU -> severitatea (pastila_firma) e aceeasi indiferent cine
    intreaba (headerul de detaliu nu mai poate fi mai bun decat ce e sub el). Cost pe calea de detaliu:
    _verificari_contabile rula deja acolo (partea grea - regenereaza D300/D112/D390); se adauga doar
    verificare_stocuri (O(articole) query-uri usoare) + intrastat_praguri (1 query). Vezi DECIZII 23.07.
    Intoarce (contabil, vc)."""
    contabil = []
    vc = None
    try:
        vc = _verificari_contabile(schema, an, luna)
        ech = vc.get("echilibru") or {}
        if not ech.get("ok", True):
            contabil.append(_flag_constatare(stare_din_nivel(ech.get("nivel")), "Balanță dezechilibrată", ech.get("mesaj"), ech.get("temei"), an, luna))
        tz = vc.get("trezorerie") or []
        tz_probleme = tz if isinstance(tz, list) else ([tz] if isinstance(tz, dict) and not tz.get("ok", True) else [])
        for p in tz_probleme:
            contabil.append(_flag_constatare(stare_din_nivel(p.get("nivel")), "Solduri creditoare trezorerie", p.get("mesaj"), p.get("temei"), an, luna))
        # [control_incrucisat_v1 + F163_ui] declaratie vs evidenta. Constatarea INTREAGA e in «Declaratie vs
        # contabilitate»; aici doar sumarul (eticheta + temei). Etichete = EXACT cele filtrate in control.js.
        for cheie, et in (("tva_incrucisat", "TVA declarat diferă de contabilitate"),
                          ("d112_incrucisat", "Salarii declarate diferă de contabilitate"),
                          ("d390_incrucisat", "Operațiuni intracomunitare declarate diferă de evidență"),
                          ("cota_tva_conformitate", "Facturi emise cu cotă TVA greșită pentru perioadă")):
            vd = vc.get(cheie) or {}
            if vd.get("stare") == "rosu":
                prima = next((c for c in (vd.get("constatari") or []) if c.get("stare") == "rosu"), {})
                contabil.append(_flag_constatare(prima.get("stare"), et, prima.get("mesaj"), prima.get("temei"), an, luna, prima.get("remediu")))
    except Exception as e:
        _verificator_esuat(contabil, "Verificări contabile — eșuate",
                           "verificările contabile (echilibru, trezorerie, declarație vs contabilitate)",
                           e, an, luna)
    # [P7 · lotul 2] Cele doua verificari sunt ele insele use-case-uri — fostele rute
    # `verificare_stocuri` si `intrastat_praguri` —, iar acum se cheama DIRECT, nu prin invelisul
    # lor HTTP. Importul e local fiindca `uc_tenants` importa la randul lui modulul asta, iar la
    # nivel de fisier cele doua s-ar bloca una pe alta. Refuzul lor iese acum ca `_erori.<Clasa>`
    # in loc de `HTTPException`; amandoua sunt `Exception`, iar cele doua `except Exception` de mai
    # jos le prind la fel — constatarea produsa e neschimbata.
    from core import uc_tenants as _uc_tenants
    try:  # stocuri contabil vs fise CV
        vs = _uc_tenants.verificare_stocuri(tid, ctx)
        if not vs.get("ok", True):
            difs = [c for c in vs.get("conturi", []) if not c.get("ok")]
            mesaj = ("Sold contabil diferit de fișele CV pe conturile: " + ", ".join(c["cont"] for c in difs) + "."
                     if difs else "Soldul contabil diferă de fișele de magazie CV.")
            # verificare_stocuri NU declara `nivel` (cauze legitime) -> stare_din_nivel(None)=gri. Vezi DECIZII 23.07.
            contabil.append(_flag_constatare(stare_din_nivel(vs.get("nivel")), "Diferențe stocuri", mesaj, vs.get("nota"), an, luna))
    except Exception as e:
        _verificator_esuat(contabil, "Verificare stocuri — eșuată", "stocurile (sold contabil vs fișe CV)", e, an, luna)
    try:  # praguri Intrastat
        ip = _uc_tenants.intrastat_praguri(tid, an, ctx)
        fluxuri = [nume for nume in ("introduceri", "expedieri") if ip[nume]["status"] != "sub_prag"]
        if fluxuri:
            # Intrastat declara nivel=AVERTISMENT (intrastat.NIVEL_STATUS) -> galben prin stare_din_nivel.
            contabil.append(_flag_constatare(stare_din_nivel(ip.get("nivel")), "Prag Intrastat depășit",
                                             "Prag Intrastat depășit pe: " + ", ".join(fluxuri) + ".",
                                             ip.get("nota"), an, luna))
    except Exception as e:
        _verificator_esuat(contabil, "Verificare Intrastat — eșuată", "pragurile Intrastat", e, an, luna)
    # [F180] regim TVA local vs snapshot ANAF (constatare structurata deja produsa de evalueaza_firma)
    rta = regim_tva_anaf or {}
    if rta.get("stare") == "rosu":
        contabil.append(_flag_constatare(rta.get("stare"), "Regim TVA diferă de ANAF", rta.get("mesaj"), rta.get("temei"), an, luna, rta.get("remediu")))
    return contabil, vc
