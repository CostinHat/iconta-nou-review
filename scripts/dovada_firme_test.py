# -*- coding: utf-8 -*-
"""scripts/dovada_firme_test.py — DOVADA PE ECRAN a reparațiilor pe firmele de test ale cabinetului de test, inclusiv pe documentele
create ÎNAINTE de reparație (comanda Costin 11.2 pct.3, verbatim: „nimic nu e «rezolvat» fără dovadă pe ecran pe firmele de test, inclusiv
pe documentele create înainte de reparație. Orice reparație acoperă și datele existente.”).

DE CE O COPIE. Lotul nepublicat nu rulează pe producție (producția servește codul publicat), deci reparațiile lui nu se pot vedea pe
firmele de test acolo. Unealta copiază firmele de test ale cabinetului „Cabinet Test Sesiunea B SRL” (F1–F7 + FISCALOS, `tenant_049` …
`tenant_055`, `tenant_057`) din PRODUCȚIE în baza de TEST, le trece prin migrările lotului exact cum le-ar trece publicarea și deschide ecranele cu
aplicația din arborele de lucru.

  --cloneaza   1. verifică în `public` (producție, numai-citire) că fiecare schemă sursă e a cabinetului de test, NU a cabinetului pilot —
                  altfel se oprește înainte de orice copiere; verifică și că nicio coloană a schemelor nu arată a secret;
               2. `pg_dump` pe fiecare schemă (numai-citire: `default_transaction_read_only`), restaurată în baza de TEST sub alt nume
                  (`tenant_9049` … `tenant_9055`: aplicația și migrările recunosc numai `tenant_<cifre>`, iar numerele 9xxx stau departe
                  de contorul firmelor plasei); a doua clonare o înlocuiește pe prima;
               3. în `public`-ul bazei de TEST: cabinetul (aceleași id-uri, numele marcat „copie de dovadă”), doi utilizatori NOI cu
                  aceleași id-uri ca pe producție (ca autorul notelor să rămână același) dar cu email sintetic și o parolă NOUĂ, generată
                  aici și ținută numai local (`~/.cache/iconta_dovada/parola`, 0600) — nicio parolă / token / cheie de producție nu se
                  copiază; firmele, legăturile utilizator-firmă și rândurile publice de care au nevoie ecranele (declarații depuse, coada,
                  tipul firmei, alertele emise; cursul BNR lipsă);
               4. migrările pe care producția încă nu le are (registrul `public.migrari_rulate` de pe producție, citit), în ordinea
                  publicării (`core.migrari_registru.in_ordine`), rulate cu `python -m core.migrari_registru ruleaza` pe baza de TEST
                  — „datele existente” trec prin aceeași migrare ca la publicare.
  --capturi=DIR  pornește aplicația din ARBORELE de lucru pe un port liber, pe baza de TEST (mecanismul lui `scripts/e2e_poarta.py`:
                  export, statica publicată lângă), se autentifică pe `/auth/login` cu utilizatorul copiei și parcurge lista de dovezi
                  (`--dovezi=FIȘIER`, implicit `frontend_test/dovada/dovezi_lot11.json`; `--doar=NR` numai acel număr): pași (citiri de
                  ecran), verificări de text, captură. Rezultatul: capturile + `DIR/dovezi.json` (ce s-a văzut pe fiecare).
               `--petic=FIȘIER.json`: un petic propus ([{"fisier", "ancora", "inlocuire"}], forma mutațiilor din `e2e_poarta.py`)
                  aplicat pe COPIA exportată, niciodată pe arborele de lucru — dovada unei reparații propuse pentru un fișier pe care
                  nu-l poți edita acum;
               `--anaf-real`: aplicația copiei întreabă serviciul public ANAF de verificare a CUI-ului (citire, ca producția), în
                  locul răspunsurilor simulate ale plasei — pentru dovezile marcate `"anaf_real": true` (444: numele de la ANAF față de
                  fișele existente); fără el, ANAF simulat răspunde „negăsit” la orice CUI.
  --sterge     scoate copia din baza de TEST (schemele 9xxx și rândurile ei publice), ca să nu rămână peste suita de teste.
  --amprente=DIR  AFIȘEAZĂ manifestul capturilor din DIR (`{"dovezi/lot<N>/<captura>.png": sha256}`), de scris în `DIR/AMPRENTE.json`.
               Capturile NU intră în index (`core/test_fara_probe_imagine.py`, decizia Costin 03.09.2026: „nu se salvează și nu devin bază
               de comparație”); intră manifestul, iar `core/test_deficiente.py` leagă fiecare captură citată în DEFICIENTE de amprenta ei.
               Imaginile călătoresc în ZIP-ul lotului.

Frontiera: pe PRODUCȚIE numai `pg_dump` și SELECT, pe o conexiune numai-citire; scrierile merg NUMAI într-o bază pe care
`core.mediu_test.motive` o acceptă ca de test (altfel refuz, cod 2). Rularea ia lacătul plasei (`scripts/e2e_poarta.LACAT`): pornirea
aplicației și migrările fac DDL pe toate firmele bazei de test, deci nu se suprapun cu o rulare e2e.

Uz: python scripts/dovada_firme_test.py --cloneaza | --capturi=DIR [--dovezi=FIȘIER] [--doar=NR[,NR…]] [--petic=F.json] [--anaf-real] | --sterge
    | --amprente=DIR
"""
import fcntl
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)
import argumente_script  # noqa: E402

#: Cabinetul firmelor de test (comanda Costin; REGULI lotul 11 „Baza de date”). Orice schemă sursă a altui cabinet = refuz.
CABINET_TEST = "Cabinet Test Sesiunea B SRL"
#: Schemele sursă (F1–F5, FISCALOS, F6) -> schema copiei în baza de test.
#: [lotul 13, comanda 13.1 pct.8] + F7 „Preluare Test SRL” (`tenant_057`, creată pe 24.10.2026 pentru grupa 1: preluarea) — dovada grupei 1
SURSE = ("tenant_049", "tenant_050", "tenant_051", "tenant_052", "tenant_053", "tenant_054", "tenant_055", "tenant_057")
PREFIX_COPIE = "tenant_9"
MARCAJ_CABINET = " — copie de dovadă"
STARE_DIR = os.path.expanduser("~/.cache/iconta_dovada")
TEMP = os.environ.get("DOVADA_TEMP", "/tmp/dovada_firme_test")
DOVEZI_IMPLICIT = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot11.json")
#: Rândurile publice copiate, pe firmă (coloanele comune ambelor baze). Restul tabelelor cu `tenant_id` nu se copiază: chei / tokene
#: (spv_token, reges_chei, api_chei), urme de acces și jurnale (audit_log, urme_portal, schimbari_email), cache-uri recalculate de aplicație
#: (firma_rezumat, firma_sursa_versiune, supervizor_*).
PUBLICE_PE_FIRMA = ("declaratii_depuse", "declaratii_coada", "firma_tip", "alerte_control_emise", "declaratii_in_asteptare")
#: Coloanele de utilizator copiate (identitatea de pe ecran și drepturile); NU: email, password_hash, telefon, sesiuni.
COLOANE_UTILIZATOR = ("nume", "prenume", "functie", "rol", "activ", "parola_schimbata", "poate_pregati", "poate_valida", "poate_depune",
                      "nivel")
#: O coloană a cărei denumire arată a secret oprește copierea (verificată pe schemele sursă înainte de `pg_dump`).
RE_SECRET = re.compile(r"(token|parola|passw|secret|api_?key|refresh|pfx|privat)", re.I)
TELEFON_TEST = "+40700000000"


class Refuz(SystemExit):
    """Refuzul uneltei, cu codul lui (structural, nu din text) și mesajul pentru om. Ieșire cu cod 2."""

    def __init__(self, cod, mesaj):
        SystemExit.__init__(self, 2)
        self.cod, self.mesaj = cod, mesaj

    def __str__(self):
        return "[dovada] %s: %s — nimic nu s-a scris." % (self.cod, self.mesaj)


def schema_copie(sursa):
    """PURĂ. `tenant_049` -> `tenant_9049`."""
    if sursa not in SURSE:
        raise Refuz("SCHEMA_NECUNOSCUTA", "%r nu e o firmă de test a cabinetului de test (%s)" % (sursa, ", ".join(SURSE)))
    return PREFIX_COPIE + sursa[len("tenant_"):]


def redenumeste(text, sursa, tinta):
    """PURĂ. Numele schemei înlocuit ca identificator întreg (`tenant_049` nu atinge `tenant_0490` / `tenant_049_x`)."""
    return re.sub(r"\b%s\b" % re.escape(sursa), tinta, text)


def tinta_de_test(env):
    """Refuză dacă mediul țintă nu e dovedit de test (`core.mediu_test.motive`). Întoarce DSN-ul bazei de test."""
    from core import mediu_test
    m = mediu_test.motive(env)
    if m:
        raise Refuz("TINTA_NU_E_DE_TEST", "; ".join("%s (%s)" % (x.cod, x.detaliu) for x in m))
    return env["DATABASE_URL"] if env.get("DATABASE_URL") else None


def verifica_surse(randuri):
    """PURĂ. `randuri` = [(tenant_id, schema, nume, cabinet_id, nume_cabinet)] citite din `public` pe producție. Refuză orice schemă
    sursă lipsă sau a altui cabinet decât `CABINET_TEST` (cabinetul pilot) și cabinetele diferite între ele. -> (cabinet_id, {schema: rând})."""
    pe_schema = {r[1]: r for r in randuri}
    lipsa = [s for s in SURSE if s not in pe_schema]
    if lipsa:
        raise Refuz("SCHEMA_LIPSA", "schemele %s nu sunt în public.tenants" % ", ".join(lipsa))
    straine = ["%s (%s, cabinetul %r)" % (s, pe_schema[s][2], pe_schema[s][4]) for s in SURSE if pe_schema[s][4] != CABINET_TEST]
    if straine:
        raise Refuz("SCHEMA_ALTUI_CABINET", "nu sunt ale cabinetului de test %r: %s" % (CABINET_TEST, "; ".join(straine)))
    cabinete = {pe_schema[s][3] for s in SURSE}
    if len(cabinete) != 1:
        raise Refuz("CABINETE_DIFERITE", "schemele sursă stau în cabinete diferite: %s" % sorted(cabinete))
    return cabinete.pop(), {s: pe_schema[s] for s in SURSE}


def coloane_secrete(coloane):
    """PURĂ. [(tabel, coloană)] -> cele care arată a secret (`RE_SECRET`)."""
    return ["%s.%s" % (t, c) for t, c in coloane if RE_SECRET.search(c)]


# ── mediul ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _env_test():
    os.environ["E2E_TEMP"] = TEMP           # înaintea importului: `e2e_poarta.TEMP` se citește la import
    import e2e_poarta
    return e2e_poarta._env_test()


def _conexiune_productie():
    import psycopg2
    from core import mediu_test
    dsn = mediu_test.dsn_productie()
    if not dsn:
        raise Refuz("PRODUCTIE_NECITITA", "DSN-ul producției nu se poate citi din %s" % mediu_test.CALE_DB_ENV)
    c = psycopg2.connect(dsn, options="-c default_transaction_read_only=on")
    c.set_session(readonly=True)
    return dsn, c


def _lacat():
    import e2e_poarta
    f = open(e2e_poarta.LACAT, "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def _stare(scrie=None):
    cale = os.path.join(STARE_DIR, "stare.json")
    if scrie is None:
        return json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else None
    os.makedirs(STARE_DIR, mode=0o700, exist_ok=True)
    json.dump(scrie, open(cale, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    return scrie


def _ceas(etape, nume, t0):
    etape.append((nume, round(time.time() - t0, 1)))
    print("[dovada] %-42s %6.1f s" % (nume, etape[-1][1]), flush=True)
    return time.time()


def _sterge_referintele(cur, tinta, ids):
    """Rândurile din `public` care trimit, prin cheie străină, la `public.<tinta>` cu unul din `ids` (copia): o dovadă care scrie pe copie
    poate lăsa rânduri în orice tabel legat de cabinet / utilizatori / firme (de ex. `migrare_status` după un import), iar scoaterea
    cabinetului s-ar opri pe cheia lor. Cheile se citesc din catalog, nu dintr-o listă scrisă de mână."""
    if not ids:
        return
    cur.execute("""SELECT cl.relname, a.attname FROM pg_constraint c JOIN pg_class cl ON cl.oid = c.conrelid
                   JOIN pg_namespace n ON n.oid = cl.relnamespace JOIN pg_class tg ON tg.oid = c.confrelid
                   JOIN pg_namespace tn ON tn.oid = tg.relnamespace JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
                   WHERE c.contype = 'f' AND n.nspname = 'public' AND tn.nspname = 'public' AND tg.relname = %s
                     AND array_length(c.conkey, 1) = 1 AND cl.relname NOT IN ('tenants', 'users')""", (tinta,))
    for tabel, col in cur.fetchall():
        cur.execute('DELETE FROM public."%s" WHERE "%s" = ANY(%%s)' % (tabel, col), (list(ids),))


# ── --sterge ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _sterge_copia(cur, cabinet_id=None, utilizatori=(), firme=()):
    """Schemele copiei și rândurile ei din `public` (numai cele marcate ale copiei: cabinetul cu `MARCAJ_CABINET`). Cu `cabinet_id` /
    `utilizatori` / `firme` (id-urile pe care copia le va lua), refuză dacă vreunul e al altcuiva în baza de test."""
    cur.execute("SELECT id FROM public.accounting_firms WHERE nume LIKE %s", ("%" + MARCAJ_CABINET,))
    cabinete = [r[0] for r in cur.fetchall()]
    for tabel, ids, col in (("users", list(utilizatori), "accounting_firm_id"), ("tenants", list(firme), "accounting_firm_id")):
        cur.execute('SELECT id FROM public."%s" WHERE id = ANY(%%s) AND (%s IS NULL OR %s <> ALL(%%s))' % (tabel, col, col),
                    (ids, cabinete or [0]))
        ocupate = [r[0] for r in cur.fetchall()]
        if ocupate:
            raise Refuz("ID_OCUPAT", "id-urile %s din public.%s sunt ale altcuiva în baza de test" % (ocupate, tabel))
    if cabinet_id is not None:
        cur.execute("SELECT id, nume FROM public.accounting_firms WHERE id = %s", (cabinet_id,))
        r = cur.fetchone()
        if r and not r[1].endswith(MARCAJ_CABINET):
            raise Refuz("ID_OCUPAT", "cabinetul %s există deja în baza de test și nu e al copiei (%r)" % (cabinet_id, r[1]))
    tinte = [schema_copie(s) for s in SURSE]
    cur.execute("SELECT id, schema_name, accounting_firm_id FROM public.tenants WHERE schema_name = ANY(%s)", (tinte,))
    straine = [r for r in cur.fetchall() if r[2] not in cabinete]
    if straine:
        raise Refuz("SCHEMA_OCUPATA", "schemele %s sunt ale altor firme din baza de test" % [r[1] for r in straine])
    cur.execute("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = c.table_schema "
                "AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = 'public' AND c.column_name = "
                "'tenant_id' AND c.table_name <> 'tenants'")
    tabele = sorted(r[0] for r in cur.fetchall())
    from core.tenant_stergere import ordinea_stergerii   # contoarele derivate la urmă: ștergerea unei surse le recrea (orfan, 22.10.2026)
    for cab in cabinete:
        cur.execute("SELECT id FROM public.tenants WHERE accounting_firm_id = %s", (cab,))
        firme_copiei = [r[0] for r in cur.fetchall()]
        for tid in firme_copiei:
            for t in ordinea_stergerii(tabele):
                cur.execute('DELETE FROM public."%s" WHERE tenant_id = %%s' % t, (tid,))
        cur.execute("DELETE FROM public.declaratii_coada WHERE cabinet_id = %s", (cab,))
        _sterge_referintele(cur, "tenants", firme_copiei)
        cur.execute("DELETE FROM public.tenants WHERE accounting_firm_id = %s", (cab,))
        cur.execute("SELECT id FROM public.users WHERE accounting_firm_id = %s", (cab,))
        uids = [r[0] for r in cur.fetchall()]
        for uid in uids:
            for t, col in (("notificari", "user_id"), ("audit_log", "user_id"), ("login_esecuri", "user_id")):
                cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name=%s AND column_name=%s",
                            (t, col))
                if cur.fetchone():
                    cur.execute('DELETE FROM public."%s" WHERE "%s" = %%s' % (t, col), (uid,))
        _sterge_referintele(cur, "users", uids)
        cur.execute("DELETE FROM public.users WHERE accounting_firm_id = %s", (cab,))
        _sterge_referintele(cur, "accounting_firms", [cab])
        cur.execute("DELETE FROM public.accounting_firms WHERE id = %s", (cab,))
    for s in tinte:
        cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % s)
    return cabinete


def sterge(_argv):
    import psycopg2
    env = _env_test()
    dsn = tinta_de_test(env)
    with _lacat():
        with psycopg2.connect(dsn) as c, c.cursor() as cur:
            cab = _sterge_copia(cur)
        for f in ("stare.json", "parola"):
            if os.path.exists(os.path.join(STARE_DIR, f)):
                os.remove(os.path.join(STARE_DIR, f))
        print("[dovada] copia scoasă din baza de test (cabinete %s, scheme %s)" % (cab, [schema_copie(s) for s in SURSE]))
    return 0


# ── --cloneaza ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _coloane(cur, tabel):
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s "
                "ORDER BY ordinal_position", (tabel,))
    return [r[0] for r in cur.fetchall()]


def _copiaza_randuri(cp, ct, tabel, unde, param, inlocuiri=None, exclude=()):
    """Rândurile `tabel` WHERE `unde` de pe producție (cp) în baza de test (ct), pe coloanele comune, cu id-ul păstrat."""
    col = [c for c in _coloane(cp, tabel) if c in set(_coloane(ct, tabel)) and c not in exclude]
    cp.execute('SELECT %s FROM public."%s" WHERE %s' % (", ".join('"%s"' % c for c in col), tabel, unde), param)
    randuri = cp.fetchall()
    from psycopg2.extras import Json
    for r in randuri:
        r = list(r)
        for i, c in enumerate(col):
            if inlocuiri and c in inlocuiri:
                r[i] = inlocuiri[c](r[i])
            if isinstance(r[i], (dict, list)):
                r[i] = Json(r[i])
        ct.execute('INSERT INTO public."%s" (%s) OVERRIDING SYSTEM VALUE VALUES (%s)' % (tabel, ", ".join('"%s"' % c for c in col),
                                                                                         ", ".join(["%s"] * len(col))), r)
    return len(randuri)


def _aliniaza_secventa(ct, tabel):
    ct.execute("SELECT pg_get_serial_sequence(%s, 'id')", ("public." + tabel,))
    sec = ct.fetchone()[0]
    if sec:
        ct.execute('SELECT setval(%%s, GREATEST((SELECT last_value FROM %s), (SELECT COALESCE(max(id), 1) FROM public."%s")))'
                   % (sec, tabel), (sec,))


def _migrari_nepublicate(cp):
    """[(fișier, amprentă)] — migrările arborelui fără rând în registrul PRODUCȚIEI, în ordinea publicării."""
    import glob
    from core import migrari_registru as mr
    migr = {}
    for p in sorted(glob.glob(os.path.join(RAD, "core", "migrare_*.py"))):
        rel = os.path.relpath(p, RAD)
        t = open(p, encoding="utf-8").read()
        if mr.e_migrare(rel, t):
            migr[rel] = mr.amprenta(t)
    return mr.nerulate(cp, migr)


def cloneaza(_argv):
    import psycopg2
    etape, t0, start = [], time.time(), time.time()
    env = _env_test()
    dsn_test = tinta_de_test(env)
    dsn_prod, cp_conn = _conexiune_productie()
    from core import mediu_test
    if mediu_test.desface_dsn(dsn_test)["dbname"] == mediu_test.desface_dsn(dsn_prod)["dbname"]:
        raise Refuz("TINTA_E_PRODUCTIA", "baza țintă are același nume ca producția")
    cp = cp_conn.cursor()
    # 1. sursele, în public pe producție
    cp.execute("SELECT t.id, t.schema_name, t.nume, t.accounting_firm_id, af.nume FROM public.tenants t "
               "LEFT JOIN public.accounting_firms af ON af.id = t.accounting_firm_id WHERE t.schema_name = ANY(%s)", (list(SURSE),))
    cabinet_id, surse = verifica_surse(cp.fetchall())
    cp.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = ANY(%s)", (list(SURSE),))
    sec = coloane_secrete(cp.fetchall())
    if sec:
        raise Refuz("COLOANA_SECRETA", "coloane care arată a secret în schemele sursă: %s" % ", ".join(sorted(set(sec))))
    tids = [surse[s][0] for s in SURSE]
    cp.execute("SELECT id FROM public.users WHERE accounting_firm_id = %s ORDER BY id", (cabinet_id,))
    utilizatori = [r[0] for r in cp.fetchall()]
    migrari = _migrari_nepublicate(cp)
    cp.execute("SELECT now()")
    clipa = cp.fetchone()[0]
    t0 = _ceas(etape, "1. surse verificate (producție, numai-citire)", t0)
    with _lacat():
        # 2. pg_dump -> baza de test, sub numele copiei
        ct_conn = psycopg2.connect(dsn_test)
        ct = ct_conn.cursor()
        _sterge_copia(ct, cabinet_id, utilizatori, tids)
        ct_conn.commit()
        t0 = _ceas(etape, "2a. copia veche scoasă", t0)
        env_dump = dict(os.environ, PGOPTIONS="-c default_transaction_read_only=on")
        for s in SURSE:
            d = subprocess.run(["pg_dump", "--schema=" + s, "--no-owner", "--no-privileges", "--dbname=" + dsn_prod],
                               capture_output=True, text=True, env=env_dump)
            if d.returncode != 0:
                raise Refuz("PG_DUMP", "%s: %s" % (s, d.stderr.strip()[-400:]))
            sql = redenumeste(d.stdout, s, schema_copie(s))
            r = subprocess.run(["psql", "-q", "-v", "ON_ERROR_STOP=1", "-1", "--dbname=" + dsn_test], input=sql, capture_output=True,
                               text=True)
            if r.returncode != 0:
                raise Refuz("RESTAURARE", "%s -> %s: %s" % (s, schema_copie(s), r.stderr.strip()[-600:]))
        t0 = _ceas(etape, "2b. pg_dump + restaurare (7 scheme)", t0)
        # 3. public: cabinetul, utilizatorii (parolă nouă, locală), firmele, legăturile, rândurile pe firmă, cursul BNR
        from core import nucleu
        parola = secrets.token_urlsafe(18)
        n = {}
        n["accounting_firms"] = _copiaza_randuri(cp, ct, "accounting_firms", "id = %s", (cabinet_id,),
                                                 {"nume": lambda v: v + MARCAJ_CABINET}, exclude=("creat_la",))
        hash_parola = nucleu.hash_parola(parola)
        email = {}
        for uid in utilizatori:
            email[uid] = "dovada.%d@sesiuneab.test" % uid
            col = [c for c in COLOANE_UTILIZATOR if c in set(_coloane(cp, "users")) & set(_coloane(ct, "users"))]
            cp.execute("SELECT %s FROM public.users WHERE id = %%s" % ", ".join(col), (uid,))
            val = cp.fetchone()
            ct.execute("INSERT INTO public.users (id, email, password_hash, accounting_firm_id, telefon, notificari_salvate_la, "
                       "bun_venit_vazut_la, %s) OVERRIDING SYSTEM VALUE VALUES (%%s, %%s, %%s, %%s, %%s, now(), now(), %s)"
                       % (", ".join(col), ", ".join(["%s"] * len(col))), (uid, email[uid], hash_parola, cabinet_id, TELEFON_TEST, *val))
        n["users"] = len(utilizatori)
        copie = {surse[s][0]: schema_copie(s) for s in SURSE}
        n["tenants"] = _copiaza_randuri(cp, ct, "tenants", "id = ANY(%s)", (tids,), {"schema_name": lambda v: schema_copie(v)},
                                        exclude=("creat_la",))
        n["user_tenants"] = _copiaza_randuri(cp, ct, "user_tenants", "tenant_id = ANY(%s) AND user_id = ANY(%s)", (tids, utilizatori))
        fara_strain = {c: (lambda v: v if v in utilizatori else None) for c in ("creat_de_id", "aprobat_de_id", "respins_de_id",
                                                                                 "depus_de_id", "trecut_de_id")}
        for t in PUBLICE_PE_FIRMA:
            n[t] = _copiaza_randuri(cp, ct, t, "tenant_id = ANY(%s)", (tids,), fara_strain if t == "declaratii_coada" else None)
        for t in ("accounting_firms", "users", "tenants", "declaratii_coada"):
            _aliniaza_secventa(ct, t)
        cp.execute("SELECT data, moneda, curs, luat_la FROM public.curs_bnr_zilnic WHERE data >= DATE '2026-01-01'")
        bnr = cp.fetchall()
        for r in bnr:
            ct.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs, luat_la) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", r)
        n["curs_bnr_zilnic (citite)"] = len(bnr)
        ct_conn.commit()
        ct_conn.close()
        cp_conn.rollback()
        cp_conn.close()
        os.makedirs(STARE_DIR, mode=0o700, exist_ok=True)
        cale_parola = os.path.join(STARE_DIR, "parola")
        fd = os.open(cale_parola, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.write(fd, parola.encode())
        os.close(fd)
        t0 = _ceas(etape, "3. public: cabinet, utilizatori, firme, rânduri", t0)
        # 4. migrările nepublicate, ca la publicare, pe baza de TEST
        rulate = []
        py = os.path.join(RAD, "venv", "bin", "python")
        for f, a in migrari:
            tm = time.time()
            r = subprocess.run([py, "-m", "core.migrari_registru", "ruleaza", f], cwd=RAD, env=dict(env, PYTHONDONTWRITEBYTECODE="1"),
                               capture_output=True, text=True)
            iesire = (r.stdout + r.stderr).strip().splitlines()
            rulate.append({"fisier": f, "amprenta": a[:12], "cod": r.returncode, "durata_s": round(time.time() - tm, 1),
                           "iesire": iesire[-6:]})
            print("[dovada]   %s (%s): cod %d — %s" % (f, a[:12], r.returncode, " | ".join(iesire[-3:])), flush=True)
            if r.returncode != 0:
                raise Refuz("MIGRARE", "%s a eșuat pe baza de test: %s" % (f, " | ".join(iesire[-6:])))
        t0 = _ceas(etape, "4. migrările nepublicate (%d)" % len(rulate), t0)
    _stare({"clonat_la": time.strftime("%Y-%m-%d %H:%M:%S"), "productie_la": clipa, "cabinet_id": cabinet_id,
            "utilizator": {"id": utilizatori[0], "email": email[utilizatori[0]]}, "utilizatori": email,
            "firme": {copie[tid]: {"tenant_id": tid, "sursa": surse[s][1], "nume": surse[s][2]} for s in SURSE for tid in [surse[s][0]]},
            "randuri_publice": n, "migrari": rulate, "etape_s": etape})
    print("[dovada] copia gata în %.0f s: %s" % (time.time() - start, ", ".join("%s=%s" % (copie[surse[s][0]], surse[s][2]) for s in SURSE)))
    print("[dovada] rânduri publice: %s" % n)
    return 0


# ── --capturi ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _port_liber():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def capturi(argv):
    stare = _stare()
    if not stare:
        raise Refuz("FARA_COPIE", "copia nu există (rulează întâi --cloneaza)")
    iesire = [a.split("=", 1)[1] for a in argv if a.startswith("--capturi=")][0]
    fis = ([a.split("=", 1)[1] for a in argv if a.startswith("--dovezi=")] or [DOVEZI_IMPLICIT])[0]
    doar = [a.split("=", 1)[1] for a in argv if a.startswith("--doar=")]
    dovezi = json.load(open(fis, encoding="utf-8"))
    if doar:
        dovezi = [d for d in dovezi if str(d["nr"]) in doar[0].split(",")]
        if not dovezi:
            raise Refuz("DOVADA_NECUNOSCUTA", "niciun număr %s în %s" % (doar[0], fis))
    env = _env_test()
    tinta_de_test(env)
    if "--anaf-real" in argv:
        env.pop("ICONTA_ANAF_SIMULAT", None)
    else:
        for d in dovezi:
            if d.get("anaf_real"):
                print("[dovada] %s cere ANAF real (fără --anaf-real răspunsul e cel simulat: „negăsit”)" % d["nr"])
    import e2e_poarta
    parola = open(os.path.join(STARE_DIR, "parola"), encoding="utf-8").read().strip()
    etape, t0 = [], time.time()
    os.makedirs(iesire, exist_ok=True)
    with _lacat():
        arb = e2e_poarta._exporta(True)
        for cale_p in [a.split("=", 1)[1] for a in argv if a.startswith("--petic=")]:
            petice = json.load(open(cale_p, encoding="utf-8"))
            for pe in (petice if isinstance(petice, list) else [petice]):
                tinta = os.path.join(arb, pe["fisier"])
                text = open(tinta, encoding="utf-8").read()
                if text.count(pe["ancora"]) != 1:
                    raise Refuz("PETIC", "ancora nu e unică în %s (de %d ori)" % (pe["fisier"], text.count(pe["ancora"])))
                open(tinta, "w", encoding="utf-8").write(text.replace(pe["ancora"], pe["inlocuire"], 1))
                print("[dovada] petic aplicat pe copie: %s" % pe["fisier"])
        py = os.path.join(RAD, "venv", "bin", "python")
        r = subprocess.run([py, "scripts/publica_static.py", "--din-arbore"], cwd=arb, env=env, capture_output=True, text=True)
        if r.returncode != 0:
            raise Refuz("STATICA", (r.stdout + r.stderr).strip()[-400:])
        for k in ("ICONTA_AI_SIMULAT", "ICONTA_ANAF_SIMULAT", "ICONTA_BON_DIR"):
            if k in env:
                os.makedirs(env[k], exist_ok=True)
        port = _port_liber()
        os.makedirs(STARE_DIR, mode=0o700, exist_ok=True)
        log = open(os.path.join(STARE_DIR, "uvicorn.log"), "w")   # lângă starea copiei, nu printre capturi (care pot intra în git)
        app = subprocess.Popen([py, "-m", "uvicorn", "main:app", "--port", str(port)], cwd=arb, env=env, stdout=log,
                               stderr=subprocess.STDOUT, start_new_session=True)
        try:
            for _ in range(120):
                if e2e_poarta._raspunde(port):
                    break
                time.sleep(2)
            else:
                raise Refuz("APLICATIA", "n-a răspuns pe %d (vezi %s/uvicorn.log)" % (port, STARE_DIR))
            t0 = _ceas(etape, "aplicația din arbore pornită (port %d)" % port, t0)
            sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
            # [495, lotul 12] pașii curăță ciornele formularelor în baza copiei: procesul lor citește aceeași bază de TEST ca aplicația
            os.environ.update(env)
            import pasi
            rez = pasi.ruleaza(dovezi, "http://127.0.0.1:%d" % port, stare["utilizator"]["email"], parola, stare["firme"], iesire,
                              emailuri=stare.get("utilizatori"))
            t0 = _ceas(etape, "dovezi parcurse (%d)" % len(rez), t0)
        finally:
            e2e_poarta._opreste(app)
            shutil.rmtree(TEMP, ignore_errors=True)
    json.dump({"copia": {k: stare[k] for k in ("clonat_la", "productie_la", "migrari")}, "etape_s": etape, "dovezi": rez},
              open(os.path.join(iesire, "dovezi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    st = {s: sum(1 for d in rez if d["stare"] == s) for s in ("indeplinita", "neindeplinita", "imposibila_azi")}
    print("[dovada] îndeplinite %(indeplinita)d · neîndeplinite %(neindeplinita)d · imposibile azi %(imposibila_azi)d" % st
          + " (din %d); detaliile în %s/dovezi.json" % (len(rez), iesire))
    return 1 if st["neindeplinita"] else 0


# ── --amprente ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def amprente_capturi(director):
    """{cale relativă la rădăcina repo: sha256} pentru fiecare `.png` din `director` (relativ la rădăcina repo)."""
    import hashlib
    out = {}
    plin = os.path.join(RAD, director)
    for nume in sorted(os.listdir(plin)) if os.path.isdir(plin) else []:
        if nume.endswith(".png"):
            with open(os.path.join(plin, nume), "rb") as f:
                out["%s/%s" % (director.rstrip("/"), nume)] = hashlib.sha256(f.read()).hexdigest()
    return out


def amprente(argv):
    director = [a.split("=", 1)[1] for a in argv if a.startswith("--amprente=")][0]
    print(json.dumps(amprente_capturi(director), indent=1, ensure_ascii=False, sort_keys=True))
    return 0


def main(argv):
    argv = argumente_script.citeste(argv, __doc__, flaguri=("--cloneaza", "--sterge", "--anaf-real"), cu_valoare=("--capturi=", "--dovezi=", "--doar=", "--petic=",
                                                                                                          "--amprente="),
                                    prefix="[dovada]")
    actiuni = [a for a in argv if a in ("--cloneaza", "--sterge") or a.startswith(("--capturi=", "--amprente="))]
    if len(actiuni) != 1:
        print("[dovada] o singură acțiune: --cloneaza, --capturi=DIR, --sterge sau --amprente=DIR — nimic nu pornește.\n%s"
              % __doc__[__doc__.index("Uz:"):].rstrip(), file=sys.stderr)
        return 2
    try:
        if actiuni[0] == "--cloneaza":
            return cloneaza(argv)
        if actiuni[0] == "--sterge":
            return sterge(argv)
        if actiuni[0].startswith("--amprente="):
            return amprente(argv)
        return capturi(argv)
    except Refuz as r:
        print(str(r), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
