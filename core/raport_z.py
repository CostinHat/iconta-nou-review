# -*- coding: utf-8 -*-
"""core/raport_z.py — unicitatea raportului Z, mutată din COD în BAZĂ.

**DE CE EXISTĂ.** Poarta R61 — *„un raport Z e unic pe casa de marcat și pe zi; a doua notă se
REFUZĂ"* — trăia numai în `main.py::_cere_z_unic`: un `SELECT`, apoi un `INSERT`. Între cele două
nu era nimic. Nu s-a văzut până la P5, fiindcă ruta care le conține era `async def` **fără niciun
`await` după citirea fișierului**, deci bucla de evenimente o rula până la capăt fără s-o
întrerupă. *Garanția exista, dar era o consecință accidentală a felului în care rulează handler-ul,
nu o proprietate a datelor.* Prima mutare a rutei pe un fir ar fi desfăcut-o în tăcere.

**CE FACE.** Un index unic PARȚIAL pe `(sursa, numar)`, exact pe sursele în care trăiește un raport
Z. Parțial, fiindcă alte surse au voie să repete un număr — o notă manuală și una de bancă pot purta
același `numar` fără să fie duplicate.

**CE NU FACE, ȘI E DECIZIA CEA MAI IMPORTANTĂ DIN MODULUL ĂSTA: nu șterge nimic, niciodată.** Dacă
o firmă are deja două rapoarte Z cu aceeași cheie, `CREATE UNIQUE INDEX` **eșuează pe firma aia**,
iar migrarea o raportează pe nume. *E purtarea corectă:* duplicatul e un document contabil deja
intrat în evidență, iar care din cele două e cel bun nu poate ști decât omul care a operat casa de
marcat. O migrare care ar alege singură ar șterge istoria cuiva ca să-și facă loc.

**Măsurat înainte de a scrie modulul ăsta** (10.09.2026, pe toate cele **20** de scheme active):
**0 rânduri** de raport Z în total, deci **0 duplicate**. Indexul intră pe teren gol. Dovada:
`masuratori/p5_val1b/DUPLICATE_Z.json`.

**Purtarea la eșec e a casei, nu inventată aici:** fiecare firmă în `SAVEPOINT`-ul ei, ca prima
eroare să nu spună „19 firme rupte" despre una singură; raport cu eșecuri per firmă; iar
`lifespan()` **refuză pornirea** dacă rămâne vreunul. Aceeași alegere ca la infrastructura P2, și
din același motiv: o aplicație care nu poate garanta ce pretinde n-are voie să servească trafic.
"""
import logging
import traceback

#: Sursele în care trăiește un raport Z. **Sursa unică** — `main.py` o importă de aici, ca poarta
#: din cod și indexul din bază să nu poată descrie două mulțimi diferite.
SURSE = ("horeca_z", "amef")

#: numele indexului, același pe toate schemele — ca verificarea să-l poată căuta, nu ghici
NUME_INDEX = "inregistrari_raport_z_unic"

_SQL_INDEX = (
    'CREATE UNIQUE INDEX IF NOT EXISTS %(nume)s ON "%(schema)s".inregistrari (sursa, numar) '
    "WHERE sursa IN (%(surse)s) AND numar IS NOT NULL")


def _log():
    return logging.getLogger("iconta")


def sql_index(schema):
    """SQL-ul indexului pentru o schemă. Expus ca să poată fi citit de gardă, nu recompus de ea."""
    return _SQL_INDEX % {
        "nume": NUME_INDEX, "schema": schema,
        "surse": ", ".join("'%s'" % s for s in SURSE)}


def aplica_index(conn, schema):
    """Creează indexul pe o schemă. Idempotent (`IF NOT EXISTS`). Ridică dacă există duplicate."""
    with conn.cursor() as cur:
        cur.execute(sql_index(schema))


def duplicate(conn, schema):
    """`[(sursa, numar, cate)]` — cheile duplicate care ar împiedica indexul. Pentru diagnostic.

    Se cheamă la eșec, ca mesajul să spună CARE sunt, nu doar că există. *Un refuz care nu numește
    ce l-a produs îl trimite pe om să caute.*
    """
    with conn.cursor() as cur:
        cur.execute(
            'SELECT sursa, numar, count(*) FROM "%s".inregistrari '
            " WHERE sursa = ANY(%%s) AND numar IS NOT NULL "
            " GROUP BY sursa, numar HAVING count(*) > 1 ORDER BY count(*) DESC" % schema,
            (list(SURSE),))
        return [tuple(r) for r in cur.fetchall()]


def migreaza(conn, doar_active=True):
    """Pune indexul pe TOATE firmele existente. Întoarce `{firme, deja, esecuri}`.

    Fiecare firmă în `SAVEPOINT`-ul ei: fără el, prima eroare SQL lasă tranzacția în
    `current transaction is aborted`, iar toate firmele următoare pică din cauza asta, nu din cauza
    lor — iar raportul ar trimite omul să caute în locul greșit.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants "
                    "WHERE (%s = false OR activ) ORDER BY id", (doar_active,))
        firme = [tuple(r) for r in cur.fetchall()]
    raport = {"firme": 0, "sarite": 0, "esecuri": []}
    for tid, schema in firme:
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT z_unic_tenant")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass(%s)", ("%s.inregistrari" % schema,))
                if cur.fetchone()[0] is None:
                    # schemă fără tabela de înregistrări (firmă abia creată, sau schemă de probă
                    # goală) — nu e un eșec, e o firmă care n-are ce apăra încă
                    cur.execute("RELEASE SAVEPOINT z_unic_tenant")
                    raport["sarite"] += 1
                    continue
            aplica_index(conn, schema)
            with conn.cursor() as cur:
                cur.execute("RELEASE SAVEPOINT z_unic_tenant")
            raport["firme"] += 1
        except Exception as e:      # noqa: BLE001 — o firmă ruptă nu oprește BUCLA; ce face
            # apelantul cu raportul e altceva (`lifespan` refuză pornirea).
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT z_unic_tenant")
                cur.execute("RELEASE SAVEPOINT z_unic_tenant")
            try:
                dup = duplicate(conn, schema)
            except Exception:       # noqa: BLE001
                dup = []
            raport["esecuri"].append({
                "tenant_id": tid, "schema": schema, "exceptie": "%s: %s" % (type(e).__name__, e),
                "duplicate": dup, "traceback": traceback.format_exc()})
    return raport


def verifica(conn, doar_active=True):
    """`{ok, lipsa, detaliu}` — că `CREATE INDEX` n-a ridicat excepție NU e destul.

    Se citește din catalogul PostgreSQL că indexul CHIAR există pe fiecare schemă cu tabela de
    înregistrări. *O migrare care se crede pe cuvânt e o migrare care nu s-a făcut.*
    """
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants "
                    "WHERE (%s = false OR activ) ORDER BY id", (doar_active,))
        firme = [tuple(r) for r in cur.fetchall()]
    lipsa, avute = [], 0
    for tid, schema in firme:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", ("%s.inregistrari" % schema,))
            if cur.fetchone()[0] is None:
                continue
            cur.execute("SELECT 1 FROM pg_indexes WHERE schemaname = %s AND indexname = %s",
                        (schema, NUME_INDEX))
            if cur.fetchone():
                avute += 1
            else:
                lipsa.append({"tenant_id": tid, "schema": schema})
    return {"ok": not lipsa, "lipsa": lipsa,
            "detaliu": "index `%s` prezent pe %d firme, lipsă pe %d"
                       % (NUME_INDEX, avute, len(lipsa))}


#: promisiunea pe care mesajul de eșec TREBUIE s-o poarte. Constantă, nu literal repetat: e o
#: proprietate a modulului — ce se întâmplă cu duplicatele —, nu o formulare a unei probe.
PROMISIUNE_TEXT = "NIMIC nu se șterge automat"


def componente_esec(raport):
    """`{numite, promisiune}` — CE trebuie să apară în mesaj, ca date, nu ca text.

    Există ca proba să poată compara randarea cu propriile ei intrări, în loc să caute șiruri
    scrise de mână într-un rezultat. *Un test care caută «firma_x» într-un mesaj păzește
    formularea; unul care cere ca fiecare component să se regăsească păzește ce trebuie spus.*
    """
    numite = []
    for e in raport.get("esecuri", []):
        numite.append(str(e["tenant_id"]))
        numite.append(str(e["schema"]))
        for t in (e.get("duplicate") or [])[:5]:
            numite.append(str(t[1]))
    return {"numite": numite, "promisiune": PROMISIUNE_TEXT}


def mesaj_esec(raport):
    """Textul care oprește pornirea, cu firmele NUMITE și cu duplicatele lor."""
    linii = []
    for e in raport["esecuri"]:
        d = e.get("duplicate") or []
        linii.append("firma %s (%s): %s%s" % (
            e["tenant_id"], e["schema"], e["exceptie"],
            (" — chei duplicate: %s" % ", ".join("%s/%s ×%d" % t for t in d[:5])) if d else ""))
    return ("[R61] unicitatea raportului Z nu s-a putut impune pe %d firme — aplicația NU "
            "pornește. Câtă vreme indexul lipsește, două încărcări simultane ale aceluiași raport "
            "Z pot intra amândouă în evidență, iar asta nu se vede la citire. %s: care din "
            "documentele duplicate e cel bun se decide de om. %s"
            % (len(raport["esecuri"]), PROMISIUNE_TEXT, " | ".join(linii)))
