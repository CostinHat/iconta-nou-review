# -*- coding: utf-8 -*-
"""core/tenant_stergere.py — R72: o firmă adăugată din greșeală se scoate; una cu evidență, nu.

DE UNDE VINE. Două firme `PROBA PORTAL SRL` create din greșeală pe 26.08.2026 au rămas în
portofoliu fiindcă **nu exista nicio cale de a scoate o firmă**. `DELETE /tenants/{id}` nu exista;
singura ștergere din aplicație era `core/gdpr_sterge.py`, care ia un **cabinet întreg**. Iar
duplicatul a costat în aceeași zi: Costin a citit *„Niciun cont de client încă"* pe firma greșită
și l-a raportat ca afirmație falsă de prag 1. Ecranul spunea adevărul; **două firme cu același
nume au făcut un ecran corect să se citească drept fals**.

CELE DOUĂ DECIZII, ale lui Costin (27.08.2026), și ele sunt structura modulului:

  (2) **Ce înseamnă «are evidență»** — cel puțin un rând în `declaratii_depuse`, în
      `declaratii_coada`, SAU orice **document emis** din schema firmei. Motivul lui:
      *„ce s-a produs pentru cineva din afară nu se poate șterge fără să rupă un lanț."*
      O firmă cu evidență **nu se șterge — se dezactivează** (`tenants.activ`).

  (1) **Ce se curăță** — **toate cele 13** tabele din `public` care poartă `tenant_id`, plus
      schema. Motivul lui: *„cele 10 fără cheie străină sunt exact cele care ar rămâne. A curăța
      doar pe cele cu FK ar însemna să lăsăm în urmă tocmai ce nimic nu leagă."*

  **ORDINEA**, cerută explicit: întâi cele 13 din `public`, **apoi** `DROP SCHEMA`. *„Dacă una
  eșuează, schema rămâne și se poate relua. Invers — cum face `gdpr_sterge` azi — schema dispare
  și rândurile rămân orfane."* Aici totul stă într-o singură tranzacție, deci eșecul dă înapoi
  tot; ordinea rămâne cea cerută, fiindcă e singura care lasă o stare reluabilă dacă tranzacția
  se sparge vreodată în bucăți.

  **ȘI GDPR FOLOSEȘTE ACEEAȘI CALE** — tot decizia lui: *„altfel avem două căi de ștergere care
  se vor rupe separat, iar una din ele e deja ruptă."* `gdpr_sterge` cheamă `sterge(...)` pentru
  fiecare firmă a cabinetului, cu `motiv="gdpr_cabinet"`, și nu-și mai ține propria listă de două
  tabele.

CE ERA RUPT LA CALEA VECHE, măsurat 27.08.2026 pe producție: `gdpr_sterge.executa` atingea **2
din 13** tabele. Iar `anunturi_cabinet` și `solicitari_client` au cheie străină cu **ON DELETE NO
ACTION**: în ziua în care un cabinet ar fi avut un anunț sau o solicitare de client, ștergerea
GDPR **ar fi eșuat cu violare de cheie străină — după** ce `DROP SCHEMA CASCADE` rulase deja pe
firmele lui. Schema dispărută, cabinetul rămas, ștergerea oprită la mijloc. N-a lovit fiindcă
amândouă tabelele au 0 rânduri: **calea n-a fost niciodată exercitată pe un caz cu conținut.**

CE NU FACE, declarat:
  - **nu șterge backup-ul off-site** (dump integral, ștergere selectivă imposibilă) — aceeași
    limită ca la GDPR, scrisă acolo.
  - **nu decide singur dacă o firmă „merită" ștearsă.** Refuză când găsește evidență și **spune
    ce a găsit**; alegerea dintre a dezactiva și a lăsa așa e a omului.
  - **nu repară orfanii deja existenți** (cei 65+2 din R50, ai unor firme dispărute înainte de
    calea asta). Ei n-au tenant, deci nu se pot scoate pe firmă.
"""
import glob
import os
import shutil

import psycopg2.extras as _E

from core import db

BON_DIR_BAZA = os.path.expanduser("~/iconta_date/bonuri")
EFACTURA_ZIP_DIR = os.environ.get("EFACTURA_ZIP_DIR", os.path.expanduser("~/iconta_nou/efactura_zip"))

# ── CE SE CURĂȚĂ ─────────────────────────────────────────────────────────────
# Cele 13 tabele din `public` care poartă `tenant_id`, măsurate 27.08.2026 pe producție.
# NU e o listă scrisă din memorie: `core/test_tenant_stergere.py` o confruntă cu
# `information_schema` la fiecare rulare a suitei. Dacă mâine apare a paisprezecea — cum a
# apărut `schimbari_email` pe 26.08 — testul pică și cere clasificarea ei. Aia e chiar lecția
# din R50: *lista se lungește la fiecare funcționalitate nouă, iar calea de ștergere nu se uita
# la ea.*
TABELE_TENANT = (
    "alerte_control_emise",
    "anunturi_cabinet",
    "audit_log",
    "declaratii_coada",
    "declaratii_depuse",
    "pachet_povestea",
    "reges_chei",
    "reges_mesaje",
    "schimbari_email",
    "solicitari_client",
    "spv_token",
    "urme_portal",
    "user_tenants",
)

# Tabele care poartă `tenant_id` și pe care ștergerea NU le atinge — cu motivul lângă fiecare.
# Fără lista asta, garda de mai sus n-ar avea unde pune o excepție legitimă și ar cere ștergerea
# a ceea ce trebuie să supraviețuiască.
NU_SE_STERG = {
    "firme_scoase": "e chiar urma ștergerii — ștearsă odată cu firma, n-ar mai rămâne nimic "
                    "care să spună că firma a existat și cine a scos-o",
}

# ── CE ÎNSEAMNĂ „ARE EVIDENȚĂ" ───────────────────────────────────────────────
# Definiția lui Costin, 27.08.2026. În `public`, cheiate pe `tenant_id`:
EVIDENTA_PUBLIC = (
    ("declaratii_depuse", "declarații depuse"),
    ("declaratii_coada", "declarații în coadă"),
)
# În schema firmei — documente care au ieșit din firmă către cineva:
EVIDENTA_SCHEMA = (
    ("inregistrari", "note contabile"),
    ("facturi", "facturi"),
    ("state_plata", "state de plată emise"),
    ("artefacte_produse", "artefacte păstrate"),
    # Ultimele trei nu sunt în enumerarea lui, și le adaug cu motivul: au plecat din firmă la fel
    # de tare ca o factură. O chitanță e la un om; e-Factura și e-Transport sunt deja la ANAF.
    # Adăugarea împinge în direcția PRUDENTĂ: mai multe firme refuzate, niciuna ștearsă din greșeală.
    ("chitante", "chitanțe"),
    ("efactura_trimiteri", "trimiteri e-Factura către SPV"),
    ("etransport_trimiteri", "notificări e-Transport"),
)

MOTIVE = {
    "scoatere_firma": "firmă scoasă din portofoliu (cere: fără evidență + confirmare pe CUI)",
    "gdpr_cabinet": "ștergerea întregului cabinet (GDPR art. 17) — cuprinde și firmele cu evidență",
}


def _firma(cur, tenant_id, blocheaza=False):
    cur.execute("SELECT id, nume, cui, schema_name, accounting_firm_id, activ "
                "FROM public.tenants WHERE id=%s" + (" FOR UPDATE" if blocheaza else ""),
                (tenant_id,))
    r = cur.fetchone()
    if not r:
        raise ValueError("firmă inexistentă")
    return r


def evidenta(conn, tenant_id, schema=None):
    """Ce a produs firma pentru cineva din afară. -> {are, detalii, motive, nedecis}.

    O TABELĂ LIPSĂ NU SE NUMĂRĂ CA ZERO. Dacă una din tabelele de mai sus nu există în schema
    firmei, funcția întoarce `are=True` cu motivul *«nu pot decide»* — refuzul e direcția sigură.
    Alternativa (zero tăcut) ar face ca o redenumire de tabelă să transforme o firmă cu evidență
    într-una ștearsă fără urmă: exact felul de eșec pe care modulul ăsta există ca să-l oprească.
    """
    detalii, motive, nedecis = {}, [], []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        f = _firma(cur, tenant_id)
        schema = schema or f["schema_name"]
        for tabel, eticheta in EVIDENTA_PUBLIC:
            cur.execute('SELECT count(*) AS n FROM public."%s" WHERE tenant_id=%%s' % tabel,
                        (tenant_id,))
            n = cur.fetchone()["n"]
            detalii[tabel] = n
            if n:
                motive.append("%d %s" % (n, eticheta))
        if not db.schema_valida(schema):
            raise ValueError("schema invalidă: %r" % schema)
        cur.execute("""SELECT table_name FROM information_schema.tables
                       WHERE table_schema=%s AND table_type='BASE TABLE'""", (schema,))
        are_tabela = {r["table_name"] for r in cur.fetchall()}
        for tabel, eticheta in EVIDENTA_SCHEMA:
            if tabel not in are_tabela:
                nedecis.append(tabel)
                continue
            cur.execute('SELECT count(*) AS n FROM "%s"."%s"' % (schema, tabel))
            n = cur.fetchone()["n"]
            detalii[tabel] = n
            if n:
                motive.append("%d %s" % (n, eticheta))
    if nedecis:
        motive.append("nu pot decide: lipsesc din schema %s tabelele %s"
                      % (schema, ", ".join(nedecis)))
    return {"are": bool(motive), "detalii": detalii, "motive": motive, "nedecis": nedecis}


def randuri_de_sters(conn, tenant_id):
    """Câte rânduri ar dispărea din fiecare din cele 13 tabele. Numai cele NEGOALE.

    Cerut de **R50 (c)**: *„previzualizarea numără rândurile înainte, ca omul să vadă ce
    dispare."* O ștergere care spune doar «se șterge tot» nu se poate confrunta cu nimic după.
    """
    out = {}
    with conn.cursor() as cur:
        for tabel in TABELE_TENANT:
            cur.execute('SELECT count(*) FROM public."%s" WHERE tenant_id=%%s' % tabel,
                        (tenant_id,))
            n = cur.fetchone()[0]
            if n:
                out[tabel] = n
    return out


def clienti_ramasi_fara_firma(conn, tenant_id):
    """Conturile de CLIENT legate de firma asta și de niciuna alta. [{id, email}]

    DE CE EXISTĂ, măsurat 27.08.2026 înainte de prima apăsare reală: ștergerea firmei ia rândurile
    din `user_tenants`, dar **nu** rândul din `users`. Un cont de client rămas fără nicio firmă e un
    orfan de aceeași speță cu cei din R44/R50 — doar că e un **om**: poate cere în continuare un
    link de logare, intră în portal și nu vede nimic. Clasa era **goală** (0 clienți fără firmă);
    prima ștergere ar fi produs primii doi.

    NU se șterge contul, se **dezactivează**: identitatea unui om nu e proprietatea unei firme
    (chiar lecția din R62), iar `activ=false` oprește magic-link-ul, care e singura ușă a portalului.
    Un cabinetist (`rol != 'client'`) nu intră aici: el ține de cabinet, nu de firmă.
    """
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT u.id, u.email FROM public.users u "
            "JOIN public.user_tenants ut ON ut.user_id = u.id "
            "WHERE ut.tenant_id = %s AND u.rol = 'client' AND u.activ "
            "  AND NOT EXISTS (SELECT 1 FROM public.user_tenants x "
            "                  WHERE x.user_id = u.id AND x.tenant_id <> %s) "
            "ORDER BY u.id", (tenant_id, tenant_id))
        return [dict(r) for r in cur.fetchall()]


def previzualizare(conn, tenant_id):
    """Ce se întâmplă dacă se apasă. Se cere ÎNAINTE de ștergere, ca omul să vadă ce pierde."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        f = _firma(cur, tenant_id)
    ev = evidenta(conn, tenant_id, f["schema_name"])
    return {
        "tenant_id": f["id"], "nume": f["nume"], "cui": f["cui"],
        "schema": f["schema_name"], "activ": f["activ"],
        "se_poate_sterge": not ev["are"],
        "evidenta": ev,
        # CONFIRMAREA E PE **CUI**, NU PE NUME — și motivul e chiar instanța care a produs
        # restanța: cele două firme de probă aveau ACELAȘI nume și CUI-uri diferite. O
        # confirmare pe nume ar fi acceptat ștergerea celeilalte.
        "confirmare_ceruta": f["cui"],
        "tabele_curatate": list(TABELE_TENANT),
        "randuri_de_sters": randuri_de_sters(conn, tenant_id),   # R50 (c)
        "clienti_de_dezactivat": clienti_ramasi_fara_firma(conn, tenant_id),
    }


def sterge(conn, tenant_id, motiv, sters_de_user_id, confirmare=None):
    """Scoate firma. Nu comite: tranzacția e a apelantului (`db.get_conn`).

    `motiv` trebuie să fie una din `MOTIVE`. `scoatere_firma` cere confirmare pe CUI și refuză
    dacă firma are evidență; `gdpr_cabinet` nu cere niciuna dintre ele, fiindcă acolo dispare
    cabinetul întreg și confirmarea s-a dat pe numele lui.
    """
    if motiv not in MOTIVE:
        raise ValueError("motiv necunoscut: %r (cele două sunt %s)" % (motiv, ", ".join(sorted(MOTIVE))))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        f = _firma(cur, tenant_id, blocheaza=True)
        schema = f["schema_name"]
        if not db.schema_valida(schema):
            raise ValueError("schema invalidă: %r" % schema)
        if motiv == "scoatere_firma":
            if (confirmare or "").strip() != (f["cui"] or "").strip():
                raise ValueError("confirmare greșită: scrie CUI-ul firmei, exact cum apare în listă")
            ev = evidenta(conn, tenant_id, schema)
            if ev["are"]:
                raise PermissionError(
                    "Firma are evidență și nu se poate șterge: %s. "
                    "O firmă care a produs documente se DEZACTIVEAZĂ, nu se șterge — "
                    "documentele rămân, firma iese din listă." % "; ".join(ev["motive"]))
        # URMA SE SCRIE ÎNAINTE de ștergeri, cât mai există de unde: numele, CUI-ul și schema
        # dispar odată cu rândul din `tenants`. `firme_scoase` NU e în `TABELE_TENANT` (vezi
        # `NU_SE_STERG`), deci supraviețuiește propriei ștergeri.
        sters = {}
        # ÎNAINTE de a rupe legăturile: cine rămâne fără nicio firmă.
        clienti = clienti_ramasi_fara_firma(conn, tenant_id)
        cur.execute(
            "INSERT INTO public.firme_scoase (tenant_id, nume, cui, schema_name, cabinet_id, "
            "motiv, scos_de_user_id) VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id, scos_la",
            (tenant_id, f["nume"], f["cui"], schema, f["accounting_firm_id"], motiv,
             sters_de_user_id))
        urma = cur.fetchone()
        # 1. cele 13 din `public` — ÎNTÂI, ca schema să rămână dacă vreuna refuză.
        for tabel in TABELE_TENANT:
            cur.execute('DELETE FROM public."%s" WHERE tenant_id=%%s' % tabel, (tenant_id,))
            sters[tabel] = cur.rowcount
        # 2. schema firmei — APOI.
        cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % schema)
        # 3. rândul firmei — la urmă: cât timp el există, `schema_name` spune ce mai e de curățat.
        cur.execute("DELETE FROM public.tenants WHERE id=%s", (tenant_id,))
        sters["tenants"] = cur.rowcount
        # 4. conturile de client rămase fără nicio firmă: DEZACTIVATE, nu șterse.
        if clienti:
            cur.execute("UPDATE public.users SET activ=false WHERE id=ANY(%s)",
                        ([c["id"] for c in clienti],))
            sters["clienti_dezactivati"] = cur.rowcount
        cur.execute("UPDATE public.firme_scoase SET randuri_sterse=%s WHERE id=%s",
                    (_E.Json(sters), urma["id"]))
    return {"tenant_id": tenant_id, "nume": f["nume"], "cui": f["cui"], "schema": schema,
            "motiv": motiv, "randuri_sterse": sters, "urma_id": urma["id"],
            "clienti_dezactivati": clienti, "scos_la": str(urma["scos_la"])}


def sterge_fisiere(schema):
    """Fișierele firmei de pe disc. Se cheamă DUPĂ ce tranzacția a fost comisă: un `rmtree` nu
    se dă înapoi, iar o tranzacție întoarsă ar lăsa firma în bază fără bonurile ei."""
    n = 0
    d = os.path.join(BON_DIR_BAZA, schema)
    if os.path.isdir(d):
        shutil.rmtree(d, ignore_errors=True)
        n += 1
    for f in glob.glob(os.path.join(EFACTURA_ZIP_DIR, "%s_*.zip" % schema)):
        try:
            os.remove(f)
            n += 1
        except OSError:
            pass
    return n


def comuta_activ(conn, tenant_id, activ, de_user_id):
    """Dezactivează / reactivează. Jumătatea care lipsea: `tenants.activ` era respectat la
    citire (`auth_api.tenantii_userului` filtrează pe toate trei rolurile) și nu-l scria nimic —
    o coloană cu jumătate de cale, aceeași formă ca `patron_nume` din R66."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        f = _firma(cur, tenant_id, blocheaza=True)
        if bool(f["activ"]) == bool(activ):
            return {"tenant_id": tenant_id, "activ": bool(activ), "schimbat": False}
        cur.execute("UPDATE public.tenants SET activ=%s WHERE id=%s", (bool(activ), tenant_id))
        cur.execute(
            "INSERT INTO public.audit_log (user_id, tenant_id, actiune, entitate, entitate_id, detalii) "
            "VALUES (%s,%s,%s,'tenant',%s,%s)",
            (de_user_id, tenant_id, "firma_activata" if activ else "firma_dezactivata",
             str(tenant_id), _E.Json({"nume": f["nume"], "cui": f["cui"]})))
    return {"tenant_id": tenant_id, "nume": f["nume"], "activ": bool(activ), "schimbat": True}
