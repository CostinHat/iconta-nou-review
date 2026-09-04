"""
core/tenant_provisioning.py — creează un tenant nou: schemă PostgreSQL + cele 21
de tabele (din template) + rândul în public.tenants + legarea userului.

Template-ul (tenant_template.sql) e generat o dată din tenant_001 (schema reală,
validată). Aici: generăm numele schemei noi, parametrizăm template-ul (înlocuim
numele schemei sursă), și provisionăm totul într-o singură tranzacție.

Pur (testabil fără DB): formeaza_schema_name, parametrizeaza_template.
DB (se dovedește pe server): creeaza_schema, provision_tenant.
"""
from __future__ import annotations
import re

from core import db

REGULI = "2026.1"
MODUL = "tenant_provisioning"

SCHEMA_SURSA = "TENANT_PLACEHOLDER"   # schema din care s-a generat template-ul
_RE_TENANT_NR = re.compile(r"^tenant_(\d+)$")


# ============================================================
#  GENERARE schema_name — PURĂ
# ============================================================
SECVENTA_SCHEMA = "public.tenant_schema_seq"


def formeaza_schema_name(n, lat=3):
    """Numărul → numele. PURĂ, testabilă fără DB."""
    return "tenant_%0*d" % (lat, int(n))


def urmator_schema_name(conn, lat=3):
    """[R79/T1, 28.08.2026] Următorul nume de schemă, dintr-un **contor care nu coboară**.

    CE ERA ÎNAINTE, și de ce s-a schimbat. Funcția lua `max(NNN)+1` peste `SELECT schema_name FROM
    public.tenants` — adică peste firmele **vii**. Când cea mai mare era ștearsă, maximul cobora și
    numărul **se refolosea**. Măsurat pe date, 27.08.2026: două rânduri din `public.firme_scoase`
    poartă `schema_name = 'tenant_019'`, pentru **două firme diferite**; `tenant_018` era, în
    aceeași zi, și schema unei firme scoase, și a uneia vii.

    Urma nu se pierdea — rândul rămâne dezambiguizat de `tenant_id`, care vine dintr-o secvență și
    nu se reciclează niciodată. Dar orice citire cheiată pe numele schemei minte, iar `firme_scoase`
    e singurul loc din `public` care referă un tenant așa. Decizia lui Costin, 28.08: **oprim
    reciclarea.**

    DE CE O SECVENȚĂ POSTGRES, și nu „prima gaură liberă" sau un rând cu maximul istoric:
    `nextval` **nu se întoarce la rollback**. Un provisioning care eșuează la jumătate arde un
    număr și merge mai departe — exact ce vrem. Un contor ținut într-un rând ar fi întors odată cu
    tranzacția, deci ar putea da același nume de două ori după un eșec, adică fix reciclarea pe
    care o repară.

    Plasa de siguranță: dacă numele generat există deja ca schemă, se ridică. Nu se caută altul —
    un contor monoton care produce o coliziune e un defect, nu o situație de tratat.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT nextval(%s)", (SECVENTA_SCHEMA,))
        n = cur.fetchone()[0]
        nume = formeaza_schema_name(n, lat)
        cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name = %s", (nume,))
        if cur.fetchone():
            raise ValueError(
                "contorul de scheme a produs %r, care există deja — secvența %s a rămas în urma "
                "bazei. Rulează `python3 -m core.migrare_schema_seq`." % (nume, SECVENTA_SCHEMA))
    return nume


# ============================================================
#  PARAMETRIZARE template — PURĂ
# ============================================================
def parametrizeaza_template(sql_template, schema_noua, schema_sursa=SCHEMA_SURSA):
    """
    Transformă template-ul (dump al schemei sursă) într-un script rulabil pentru
    schema nouă: înlocuiește numele schemei + scoate meta-comenzile psql (\\...)
    și resetarea search_path (inofensivă, dar evităm efecte pe conexiune).
    """
    linii = []
    for ln in sql_template.splitlines():
        s = ln.strip()
        if s.startswith("\\"):                       # \restrict, \unrestrict, etc.
            continue
        if "set_config('search_path'" in s:           # nu atingem search_path conexiunii
            continue
        linii.append(ln)
    sql = "\n".join(linii)
    # înlocuiește numele schemei (prefix calificat: schema.tabela + CREATE SCHEMA)
    sql = sql.replace(schema_sursa, schema_noua)
    return sql


# ============================================================
#  CREARE schemă — DB (se dovedește pe server)
# ============================================================
def creeaza_schema(conn, schema_noua, sql_template):
    """Rulează SQL-ul parametrizat care creează schema + tabelele. Nu face commit
    (lasă tranzacția deschisă pentru provision_tenant)."""
    if not db.schema_valida(schema_noua):
        raise ValueError("schema invalidă: %r" % schema_noua)
    sql = parametrizeaza_template(sql_template, schema_noua)
    with conn.cursor() as cur:
        cur.execute(sql)


# ============================================================
#  PROVISION tenant — orchestrare, o singură tranzacție
# ============================================================
def cui_valid(cui):
    """True daca CUI-ul are cifra de control corecta (algoritm oficial ANAF, Codul
    fiscal). Pur, testabil. Acceptata forma cu/fara prefix RO si cu spatii - se
    extrag doar cifrele. CUI romanesc: 2-10 cifre (numar identificare 1-9 + control)."""
    c = "".join(ch for ch in str(cui or "") if ch.isdigit())
    if not (2 <= len(c) <= 10):
        return False
    ponderi = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    s = sum(int(corp[i]) * ponderi[i] for i in range(9))
    r = (s * 10) % 11
    if r == 10:
        r = 0
    return r == ctrl


def nume_normalizat(nume):
    """Numele unei firme, adus la forma pe care o comparăm: spații colapsate, fără majuscule.

    NU normalizează forma juridică („SRL" vs „S.R.L.") — o normalizare mai agresivă ar refuza
    firme care chiar sunt diferite, iar refuzul fals e mai scump aici decât duplicatul: pe
    duplicat omul apasă din nou, pe refuz fals nu poate deloc.
    """
    return " ".join((nume or "").split()).casefold()


def cere_nume_unic(conn, nume, accounting_firm_id, exclude_id=None):
    """[nume_unic_v1, 27.08.2026] Un nume de firmă o singură dată per cabinet.

    Costin: *„nici Registrul Comerțului, nici ANAF nu permit. O denumire de firmă e unică în
    România — deci două rânduri cu același nume în portofoliul unui cabinet sunt un fapt
    imposibil în realitate."*

    Iar costul l-am plătit deja: pe duplicatul din 26.08 a căzut diagnosticul de la pasul 8 al
    probei R62 — un ecran corect (*„Niciun cont de client încă"*) a fost citit ca fals, fiindcă
    se deschisese cealaltă firmă cu același nume.

    Se aplică ȘI la redenumire, nu doar la creare: altfel regula s-ar putea ocoli cu un `PUT`.
    """
    n = nume_normalizat(nume)
    if not n:
        raise ValueError("Denumirea firmei nu poate fi goală")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, nume FROM public.tenants "
            "WHERE accounting_firm_id = %s AND lower(btrim(regexp_replace(nume, '\\s+', ' ', 'g'))) = %s "
            "  AND (%s::int IS NULL OR id <> %s)",
            (accounting_firm_id, n, exclude_id, exclude_id))
        r = cur.fetchone()
    if r:
        raise ValueError(
            "Ai deja în portofoliu o firmă cu denumirea „%s” (CUI-ul o deosebește, denumirea nu). "
            "O denumire de firmă e unică la Registrul Comerțului, deci două firme cu același "
            "nume nu pot exista. Verifică dacă n-ai adăugat-o deja." % r[1])


def provision_tenant(conn, nume, cui, accounting_firm_id, user_id, sql_template, tip_firma="srl"):
    # cui_control_v1: cifra de control CUI validata OFFLINE, inainte de orice - ANAF
    # (anaf_api.valideaza_cui) e best-effort in rutele de register (except: pass), deci
    # cand ANAF e jos un CUI malformat ajungea tenant real -> sparge toate declaratiile
    # ulterioare (RegistrationNumber D406/D394 etc. cer CUI valid). Algoritmul e obiectiv
    # (lege), nu depinde de disponibilitatea ANAF.
    if not cui_valid(cui):
        raise ValueError("CUI invalid: cifra de control nu corespunde (%r)" % cui)
    # cui_unic_v1: un CUI o singura data per cabinet
    with conn.cursor() as _c:
        _c.execute("SELECT id FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s",
                   (str(cui), accounting_firm_id))
        if _c.fetchone():
            raise ValueError("Firma cu acest CUI exista deja in portofoliu")
    # nume_unic_v1: si denumirea, o singura data per cabinet (vezi `cere_nume_unic`)
    cere_nume_unic(conn, nume, accounting_firm_id)
    """
    Creează un tenant complet, totul-sau-nimic:
      1. generează schema_name nou (tenant_NNN)
      2. creează schema + 21 tabele (din template)
      3. INSERT în public.tenants
      4. INSERT în public.user_tenants (leagă userul care creează)
    Întoarce {ok, tenant_id, schema_name} sau ridică excepție (apelantul face rollback).
    """
    import psycopg2.extras as _E
    # [R79/T1] Numele vine dintr-un contor care NU coboară. Nu se mai citesc firmele vii: exact
    # citirea aia făcea numărul să se refolosească după o ștergere.
    schema_noua = urmator_schema_name(conn)

    # 2) schema + tabele
    creeaza_schema(conn, schema_noua, sql_template)

    # 3) rândul în public.tenants
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, activ) "
            "VALUES (%s,%s,%s,%s,true) RETURNING id",
            (schema_noua, nume, cui, accounting_firm_id))
        tenant_id = cur.fetchone()["id"]
        # 4) leagă userul care creează (acces imediat)
        cur.execute(
            "INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s,%s) "
            "ON CONFLICT DO NOTHING",
            (user_id, tenant_id))
    # profil_la_provisionare_v1: profil minim (numerotare facturi functionala din prima)
    # [tip_firma_v1] tip_firma (srl/pfa) decide straturii de migrare + cardurile vizibile.
    # CHECK (srl/pfa) pe coloana: normalizam prin primitiva (default srl la lipsa), validam la {srl,pfa}.
    from core.migrare_api import tip_firma_nrm  # default 'srl' -> UNICA primitiva, nu literal inline
    _tip = tip_firma_nrm(tip_firma)
    if _tip not in ("srl", "pfa"):
        _tip = "srl"
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO {schema_noua}.firma_profil (id, nume, cui, serie_factura, urmator_numar_factura, tip_firma) "
            "VALUES (1, %s, %s, '', 1, %s) ON CONFLICT (id) DO NOTHING",
            (nume, str(cui), _tip))
    return {"ok": True, "tenant_id": tenant_id, "schema_name": schema_noua}


def precompleteaza_din_anaf(conn, schema_name, cui, seteaza_nume=False):
    """[F188/register_profil_anaf] SURSA UNICA de precompletare a firma_profil din ANAF v9, pentru
    TOATE caile de creare a unei firme: register (firma proprie), adaugare manuala, import in masa.
    Inainte, fiecare cale scria un subset DIFERIT (register: snapshot TVA + data inceput; add-firm:
    reg_com + tva_la_incasare; import in masa: nimic) -> data inregistrarii TVA aparea la unele firme
    si la altele nu (ruptura pe cale, nu pe camp). Aici scriu ACELASI set peste tot, o singura data.

    seteaza_nume=True doar la firma proprie (register), unde denumirea vine de la ANAF; la add-firm/
    import numele e pus de contabil si NU se atinge. COALESCE: gol de la ANAF nu suprascrie.
    Best-effort la nivel de apelant: ANAF jos -> exceptie propagata, profilul ramane pe default,
    corectabil din Date firma. Intoarce True daca a precompletat, False daca ANAF n-a gasit CUI-ul.
    NU scrie tip_decont (periodicitatea TVA): ANAF v9 nu o intoarce -> ramane alegerea contabilului
    (necunoscut declarat explicit, nu fabricat)."""
    from core import anaf_api
    cuic = str(cui).replace("RO", "").strip()
    rez = anaf_api.valideaza_cui([cuic])
    if not (rez and rez[0].get("gasit")):
        return False
    d = rez[0]
    # [nume_anaf_v1, 27.08.2026] Denumirea de la ANAF se PASTREAZA intotdeauna, cu data ei, pe
    # `public.tenants` — chiar si cand `seteaza_nume=False`, adica la add-firm si import, unde
    # numele afisat e al contabilului. Pana azi denumirea ANAF nu se retinea nicaieri: de-aia
    # „firma cu CUI validat la ANAF" nu insemna „denumire de la ANAF", iar campul se putea edita
    # liber fara sa se loveasca de nimic. Decizia lui Costin: varianta (b) — se pastreaza amandoua.
    _den = (d.get("denumire") or "").strip()
    if _den:
        with conn.cursor() as _c:
            _c.execute("UPDATE public.tenants SET nume_anaf=%s, nume_anaf_la=now() "
                       "WHERE schema_name=%s", (_den, schema_name))
    # [R81/O4, 28.08.2026] A PATRA cale care scria denumirea într-un singur loc, găsită de garda
    # de simetrie — nu de citire. `seteaza_nume=True` (numai la `POST /auth/register`, firma proprie
    # a cabinetului) scria `firma_profil.nume` singur, la câteva milisecunde după ce
    # `provision_tenant` pusese ACEEAȘI valoare în amândouă locurile. Adică divergența chiar SE
    # putea naște la creare, pe calea aia — exact ce scria R81 că nu se poate.
    #
    # Trece acum prin scriitorul unic, fără poarta de unicitate: la `register` cabinetul e abia
    # creat, iar firma e prima și singura din el, deci n-are cu ce să se ciocnească. Un refuz acolo
    # ar opri o înregistrare din cauza unei firme care nu există.
    if seteaza_nume and _den:
        with conn.cursor() as _c:
            _c.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema_name,))
            _r = _c.fetchone()
        if _r:
            scrie_denumirea(conn, _r[0], _den, verifica_unicitatea=False)
    seturi, par = [], []
    seturi += [
        "caen = COALESCE(NULLIF(%s, ''), caen)",
        "adresa = COALESCE(NULLIF(%s, ''), adresa)",
        "reg_com = COALESCE(NULLIF(%s, ''), reg_com)",
        "platitor_tva = %s",
        "tva_la_incasare = %s",
        "platitor_tva_anaf = %s",           # snapshot ANAF (verde) = aceeasi valoare la onboarding
        "platitor_tva_anaf_data = CURRENT_DATE",
        "platitor_tva_anaf_inceput = %s",   # data inregistrarii in scopuri de TVA (Q9)
    ]
    par += [
        (d.get("cod_caen") or "").strip(),
        (d.get("adresa") or "").strip(),
        (d.get("nr_reg_com") or "").strip(),
        bool(d.get("platitor_tva")),
        bool(d.get("tva_la_incasare")),
        bool(d.get("platitor_tva")),
        d.get("tva_data_inceput"),
    ]
    with conn.cursor() as cur:
        cur.execute('UPDATE "%s".firma_profil SET ' % schema_name + ", ".join(seturi), tuple(par))
    return True


# ============================================================
#  CITIRE / EDITARE — DB
# ============================================================
def detalii_tenant(conn, tenant_id):
    """Detaliile unui tenant (sau None). Apelantul verifică deja accesul."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, schema_name, nume, cui, accounting_firm_id, activ, "
            "plan_importat_la, balanta_importata_la, salariati_importati_la, "
            # [R77] Ecranul de date nu poate arăta divergența dacă n-o primește.
            "nume_anaf, nume_anaf_la, nume_ales, nume_ales_la "
            "FROM public.tenants WHERE id = %s", (tenant_id,))
        r = cur.fetchone()
    return dict(r) if r else None


ALEGERI_NUME = ("aplicatie", "anaf")


def scrie_denumirea(conn, tenant_id, nume, verifica_unicitatea=True):
    """[R81, DECIS 28.08.2026 — SIMETRIE DE SCRIERE] Denumirea unei firme se scrie în **amândouă**
    locurile, în **aceeași tranzacție**, cu **aceeași valoare**.

    Decizia lui Costin: *„orice act care redenumește o firmă scrie denumirea în AMBELE locuri
    (`public.tenants.nume` și `{schema}.firma_profil.nume`), în aceeași tranzacție, cu aceeași
    valoare. Nu se construiește alias."*

    DE CE O SINGURĂ FUNCȚIE, și nu câte o pereche de `UPDATE`-uri în fiecare cale. Trei căi
    redenumeau azi o firmă, iar fiecare atingea **un singur loc din două** — de aici R81. Trei
    perechi scrise separat s-ar putea despărți la fel de tăcut ca cele trei scrieri singure; a opta
    instanță a aceleiași lecții (R62: *regula era în două locuri și diferită*). Aici perechea e
    **un singur act**, iar `core/test_simetrie_denumire.py` pică dacă apare un `UPDATE … SET nume=`
    pe una din tabele fără perechea lui în aceeași funcție.

    POARTA DE UNICITATE rămâne pe traseu: `cere_nume_unic` se cheamă **înainte** de amândouă
    scrierile, ca o redenumire să nu poată ocoli ce refuză crearea. `verifica_unicitatea=False`
    există pentru un singur caz declarat — precompletarea de la `POST /auth/register`, unde firma e
    prima și singura din cabinetul abia creat, deci n-are cu ce să se ciocnească.

    CE NU FACE: nu consemnează alegerea (aia e `_consemneaza_alegerea`, chemată de apelanți) și nu
    comite — apelantul deține tranzacția, fiindcă simetria **este** proprietatea tranzacției.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name, accounting_firm_id FROM public.tenants WHERE id = %s",
                    (tenant_id,))
        r = cur.fetchone()
    if not r:
        raise ValueError("firmă inexistentă")
    schema_name, cabinet = r
    nume = (nume or "").strip()
    if not nume:
        raise ValueError("denumirea firmei nu poate fi goală")
    if verifica_unicitatea:
        cere_nume_unic(conn, nume, cabinet, exclude_id=tenant_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.tenants SET nume = %s WHERE id = %s", (nume, tenant_id))
        cur.execute('UPDATE "%s".firma_profil SET nume = %%s WHERE id = 1' % schema_name,
                    (nume,))
    return schema_name


def alege_cui(conn, tenant_id, cui):
    """Scrie CUI-ul firmei in AMANDOUA locurile, in aceeasi tranzactie. Sora lui `alege_denumirea`.

    [lotul 6, 04.09.2026] R81 a inchis clasa „un lucru al firmei, doua locuri, o singura scriere"
    pentru DENUMIRE. Proba de azi a aratat ca **CUI-ul era in aceeasi situatie si nimeni n-o
    numise**: ecranul „Date firma" scria numai `firma_profil.cui`, iar `public.tenants.cui` ramanea
    cel de la infiintare. Divergenta se producea tacut, iar CUI-ul intra in fiecare declaratie.

    Ca si acolo: **nu comite** — apelantul detine tranzactia, fiindca simetria ESTE proprietatea
    tranzactiei."""
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE id = %s", (tenant_id,))
        r = cur.fetchone()
    if not r:
        raise ValueError("firmă inexistentă")
    schema_name = r[0]
    with conn.cursor() as cur:
        cur.execute("UPDATE public.tenants SET cui = %s WHERE id = %s", (cui, tenant_id))
        cur.execute('UPDATE "%s".firma_profil SET cui = %%s WHERE id = 1' % schema_name, (cui,))
    return schema_name


def _consemneaza_alegerea(conn, tenant_id, alege, user_id, nume, nume_anaf):
    """Scrie CE s-a ales, CÂND și de CINE. Un singur loc pentru amândouă căile.

    Există separat de `alege_denumirea` fiindcă alegerea se poate face în **două** feluri:
    apăsând un buton în caseta de divergență, sau **tastând** o denumire diferită de cea de la
    ANAF. A doua e tot un act deliberat — Costin, 27.08: *„editarea liberă, fără să treacă prin
    întrebare, nu mai are rost… se consemnează ca alegere deliberată, cu autor."*
    """
    with conn.cursor() as cur:
        cur.execute("UPDATE public.tenants SET nume_ales=%s, nume_ales_la=now(), nume_ales_de=%s "
                    "WHERE id=%s", (alege, user_id, tenant_id))
        cur.execute(
            "INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, entitate_id, detalii) "
            "VALUES (%s, (SELECT id FROM public.tenants WHERE id = %s), 'nume_ales', 'tenant', %s, %s)",
            (user_id, tenant_id, str(tenant_id),
             __import__("json").dumps({"alege": alege, "nume": nume, "nume_anaf": nume_anaf})))


def alege_denumirea(conn, tenant_id, alege, user_id):
    """[R77] Alegerea între denumirea din aplicație și cea de la ANAF, ca **act**.

    Costin: *„«a păstra pe a ta = a nu face nimic» nu e o alegere. Cine nu apasă nimic nu decide —
    moștenește ce era acolo, și nu află niciodată că a fost o divergență."*

    Amândouă ramurile **scriu** ceva: `anaf` schimbă denumirea (prin aceleași porți ca o
    redenumire), `aplicatie` o păstrează — dar consemnează că a fost păstrată **deliberat**.
    Fără a doua, tăcerea ar fi arătat identic cu o decizie.

    O citire ANAF mai NOUĂ decât alegerea **redeschide** întrebarea: alegerea de azi nu acoperă o
    denumire care se schimbă la registru mâine.
    """
    if alege not in ALEGERI_NUME:
        raise ValueError("alegere necunoscută: %r (cele două sunt %s)"
                         % (alege, ", ".join(ALEGERI_NUME)))
    with conn.cursor() as cur:
        cur.execute("SELECT nume, nume_anaf, accounting_firm_id FROM public.tenants WHERE id=%s",
                    (tenant_id,))
        r = cur.fetchone()
    if not r:
        raise ValueError("firmă inexistentă")
    nume, nume_anaf, cabinet = r
    if alege == "anaf":
        if not (nume_anaf or "").strip():
            raise ValueError("nu există o denumire de la ANAF pentru firma asta")
        # [R81/O2, 28.08.2026] Până azi ramura asta scria NUMAI `public.tenants.nume`, deci
        # „alegerea consemnată nu ajungea pe hârtie": pe declarații pleca mai departe denumirea
        # fiscală veche. Sub simetrie, butonul schimbă denumirea în amândouă locurile, într-o
        # singură tranzacție. `cere_nume_unic` e înăuntru, deci poarta de unicitate n-a slăbit.
        scrie_denumirea(conn, tenant_id, nume_anaf)
        nume = nume_anaf
    _consemneaza_alegerea(conn, tenant_id, alege, user_id, nume, nume_anaf)
    return {"tenant_id": tenant_id, "alege": alege, "nume": nume}


def actualizeaza_tenant(conn, tenant_id, nume=None, cui=None, user_id=None):
    """Editează nume/cui (NU schema_name — fix). Întoarce {ok}.

    [27.08.2026] Până azi funcția asta era un `UPDATE` gol de orice poartă: nici cifra de control
    a CUI-ului, nici unicitatea lui, nici a numelui. Adică **toate** verificările de la creare se
    puteau ocoli cu o singură redenumire. Costin a întrebat *„de ce se poate schimba denumirea
    unei firme cu CUI validat la ANAF?"* — răspunsul e că nu exista nimic care s-o oprească.
    Acum trec pe aceleași porți ca la creare: **o regulă care se poate ocoli nu e o regulă.**
    """
    with conn.cursor() as cur:
        cur.execute("SELECT accounting_firm_id, nume_anaf FROM public.tenants WHERE id = %s",
                    (tenant_id,))
        r = cur.fetchone()
    if not r:
        raise ValueError("firmă inexistentă")
    cabinet, nume_anaf = r
    if cui is not None:
        if not cui_valid(cui):
            raise ValueError("CUI invalid: cifra de control nu corespunde (%r)" % cui)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.tenants "
                        "WHERE cui = %s AND accounting_firm_id = %s AND id <> %s",
                        (str(cui), cabinet, tenant_id))
            if cur.fetchone():
                raise ValueError("Firma cu acest CUI exista deja in portofoliu")
    if nume is None and cui is None:
        return {"ok": True, "neschimbat": True}
    # [R81/O1, 28.08.2026] Denumirea trece prin scriitorul UNIC — `public.tenants.nume` și
    # `firma_profil.nume`, aceeași tranzacție, aceeași valoare. `cere_nume_unic` e înăuntrul lui,
    # deci poarta de unicitate rămâne pe calea de redenumire, unde a fost pusă.
    #
    # CUI-ul a ieșit din `SET`-ul compus la rulare și are acum instrucțiunea lui, literală. Nu e
    # cosmetică: un `SET` asamblat din bucăți nu poate fi citit static, deci garda de simetrie
    # n-ar fi putut spune despre el nici că scrie denumirea, nici că n-o scrie — și ar fi trebuit
    # să-l declare drept necunoscut. Aici nu mai e nimic de declarat.
    if nume is not None:
        scrie_denumirea(conn, tenant_id, nume)
    if cui is not None:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.tenants SET cui = %s WHERE id = %s", (cui, tenant_id))
    # [R77, partea a doua] O redenumire care se depărtează de denumirea de la ANAF e ea însăși o
    # alegere — se consemnează, nu se refuză. Dacă firma n-are `nume_anaf`, nu se consemnează
    # nimic: n-are cu ce să difere, iar o alegere între o denumire și nimic n-ar fi o alegere.
    if nume is not None and (nume_anaf or "").strip():
        acelasi = nume_normalizat(nume) == nume_normalizat(nume_anaf)
        _consemneaza_alegerea(conn, tenant_id, "anaf" if acelasi else "aplicatie",
                              user_id, nume, nume_anaf)
    return {"ok": True}
