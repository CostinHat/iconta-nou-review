# -*- coding: utf-8 -*-
"""core/supervizor_cache.py — rezultatul supervizorului, calculat o dată și citit ieftin.

**DE CE EXISTĂ, și ce decizie înlocuiește.** `supervizor.ruleaza_portofoliu` recalculează la fiecare
chemare și nu persistă nimic — scris deliberat, citându-l pe Costin (01.09.2026): *„constatări
deschise = ce produce rularea curentă, recalculat la cerere. Fără tabel nou, fără ciclu de viață"*.
Docstringul lui numea și condiția în care asta se schimbă: *„un ciclu de viață devine necesar abia
când există consumatorul lui: stratul asistentului și **urmărirea performanței**"*.

Consumatorul a apărut (P1, 08.09.2026). Decizia nu se contrazice tăcut — se **înlocuiește**, cu
condiția ei îndeplinită, și se scrie în `DECIZII.md`.

**MĂSURAT ÎNAINTE** (reperul, pe portofoliul real de 20 de firme, cu date subțiri): 9 ms/firmă,
p95 12 ms → **~5 s la 1000 de firme, secvențial**. Ținta cerută e p95 sub 1 s. Deci nu e o
optimizare speculativă: la ținta cerută, calea de azi nu încape.

**CUM.** Trei propoziții, și fiecare e o decizie:

1. **Versiunea sursei e un CONTOR, nu o amprentă recalculată la citire.** Dacă la fiecare citire aș
   recalcula o amprentă per firmă, aș face 1000 de interogări ca să aflu dacă trebuie să fac 1000 de
   calcule — adică exact ce vreau să evit. Contorul se ridică la SCRIERE, de trigger, deci citirea e
   o singură interogare pentru tot portofoliul.

2. **Prospețimea se DERIVĂ, nu se stochează.** Nu există coloană `stare`. Un rezultat e curent
   dacă `versiune_sursa == sursa.versiune`, comparație făcută în aceeași interogare. O coloană
   `stare` ar fi a doua sursă de adevăr pentru aceeași propoziție — și prima care rămâne în urmă.

3. **Triggerele sunt mecanismul, nu apelurile din aplicație.** Un cârlig pus în modulele care scriu
   se poate uita la următoarea cale de scriere; un trigger nu poate fi ocolit. *Auditul de ieri a
   arătat de câte ori am ratat o cale de scriere căutând-o cu ochii.*

**CE NU ESTE PERMIS, și e chiar interdicția cerută:** o valoare veche NU se arată ca fiind curentă.
Citirea întoarce întotdeauna `stare` ∈ {`curent`, `invalidat`, `lipseste`}, plus `calculat_la` și
ambele versiuni. Un rezultat `invalidat` se arată — util, fiindcă e ultima măsurătoare bună — dar
**etichetat**, niciodată tăcut.

**FAULT-CHECK.** Dacă datele sursă se schimbă în timp ce rezultatul e citit, cititorul nu primește o
stare parțial actualizată, din două motive care se sprijină reciproc:
  * rezultatul unei firme e **o singură valoare `jsonb`**, scrisă printr-o singură instrucțiune
    (`INSERT … ON CONFLICT`) — nu există momentul în care jumătate din el e nou;
  * citirea e **o singură interogare, într-o singură tranzacție**, deci vede un instantaneu
    consistent (MVCC): ori perechea veche (rezultat vechi + versiune veche → `curent`), ori cea nouă
    (rezultat vechi + versiune nouă → `invalidat`). **Nu există combinație care să arate un rezultat
    vechi ca fiind curent.**
"""
from __future__ import annotations

import json

#: Tabelele-SURSĂ, derivate mecanic din ce citește `supervizor._culege_firma` (prin cele patru
#: perechi din `control_incrucisat`), nu scrise din memorie. O atingere a oricăreia invalidează
#: rezultatul firmei.
TABELE_TENANT = ("clienti", "efactura_trimiteri", "facturi", "firma_profil",
                 "inregistrari", "inregistrari_linii",
                 # [P2, 08.09.2026] Sursele MODELULUI DE CITIRE al portofoliului
                 # (`core/firma_rezumat.py`). Contorul ramane UNUL SINGUR per firma: unul per
                 # aspect ar cere N triggere per tabel si N join-uri la citire. Pretul e
                 # SUPRA-invalidarea — o scriere in `plan_conturi` invalideaza si rezultatul
                 # supervizorului, care nu depinde de el. *Supra-invalidarea inseamna munca in
                 # plus, niciodata o valoare veche aratata drept curenta.*
                 "plan_conturi", "solduri_initiale")

#: Sursa din `public`, per firmă.
TABELE_PUBLIC = ("declaratii_depuse_curente",)

#: CE NU SE URMĂREȘTE, declarat: `public.tenants` și `public.accounting_firms` sunt citite de
#: culegere, dar poartă DENUMIREA și cabinetul, nu faptele din care ies constatările. O redenumire
#: de firmă n-are voie să invalideze 1000 de rezultate. *Se scrie aici ca să fie o alegere, nu o
#: omisiune.*
NEURMARITE = ("tenants", "accounting_firms")

CURENT, INVALIDAT, LIPSESTE = "curent", "invalidat", "lipseste"

DDL = """
CREATE TABLE IF NOT EXISTS public.supervizor_sursa (
    tenant_id    integer PRIMARY KEY,
    versiune     bigint      NOT NULL DEFAULT 1,
    schimbat_la  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.supervizor_rezultat (
    tenant_id      integer     NOT NULL,
    an             integer     NOT NULL,
    luna           integer     NOT NULL,
    rezultat       jsonb       NOT NULL,
    versiune_sursa bigint      NOT NULL,
    calculat_la    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, an, luna)
);

-- Contorul se ridică la SCRIERE. `tenant_id` vine ca argument de trigger, fixat la creare:
-- triggerul rulează în schema firmei, unde `tenant_id` nu e o coloană a fiecărui tabel.
CREATE OR REPLACE FUNCTION public.supervizor_marcheaza() RETURNS trigger AS $$
DECLARE tid integer := TG_ARGV[0]::integer;
BEGIN
    INSERT INTO public.supervizor_sursa (tenant_id, versiune, schimbat_la)
         VALUES (tid, 1, now())
    -- upsert-ok: contorul E o valoare care se suprascrie prin definiție — fiecare scriere în
    -- sursă îl incrementează. Nu există „date ale utilizatorului" de pierdut aici.
    ON CONFLICT (tenant_id) DO UPDATE
            SET versiune = public.supervizor_sursa.versiune + 1, schimbat_la = now();
    RETURN NULL;   -- AFTER trigger: valoarea întoarsă e ignorată
END;
$$ LANGUAGE plpgsql;
"""


def aplica_ddl(conn):
    """Tabelele + funcția de trigger. Idempotent."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def _tenant_id_din_schema(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (schema,))
        r = cur.fetchone()
    return r[0] if r else None


def leaga_triggerele(conn, schema, tenant_id):
    """Pune triggerele pe tabelele-sursă ale unei firme. Idempotent (DROP … IF EXISTS, apoi CREATE).

    STATEMENT-level, nu ROW: contorul trebuie să crească o dată per scriere, nu o dată per rând —
    un import de 5.000 de facturi n-are de ce să ridice contorul de 5.000 de ori.

    Pune și SĂMÂNȚA contorului. Fără ea, o firmă în care nu s-a scris niciodată n-ar avea rând în
    `supervizor_sursa`, iar `de_recalculat` — care pleacă de la acel tabel — n-ar vedea-o **niciodată**:
    rezultatul ei ar rămâne `lipseste` la infinit, iar lucrătorul ar raporta „0 invalidate" despre un
    portofoliu necalculat. *Un zero care înseamnă „n-am ce face" arată exact ca unul care înseamnă
    „totul e la zi".*"""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.supervizor_sursa (tenant_id) VALUES (%s) "
            "ON CONFLICT (tenant_id) DO NOTHING", (tenant_id,))
        for t in TABELE_TENANT:
            cur.execute("SELECT to_regclass(%s)", ("%s.%s" % (schema, t),))
            if cur.fetchone()[0] is None:
                continue                       # tabelul nu există în schema asta — nu se inventează
            nume = "trg_supervizor_%s" % t
            cur.execute('DROP TRIGGER IF EXISTS %s ON "%s".%s' % (nume, schema, t))
            cur.execute(
                'CREATE TRIGGER %s AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON "%s".%s '
                "FOR EACH STATEMENT EXECUTE FUNCTION public.supervizor_marcheaza(%d)"
                % (nume, schema, t, tenant_id))


def marcheaza_schimbat(conn, tenant_id):
    """Ridică manual contorul. Pentru sursele din `public` și pentru probe."""
    with conn.cursor() as cur:
        cur.execute(
            # upsert-ok: același contor, aceeași justificare ca în trigger — se incrementează,
            # nu se suprascriu date.
            "INSERT INTO public.supervizor_sursa (tenant_id, versiune, schimbat_la) "
            "VALUES (%s, 1, now()) ON CONFLICT (tenant_id) DO UPDATE "
            "SET versiune = public.supervizor_sursa.versiune + 1, schimbat_la = now()",
            (tenant_id,))


def versiune_sursa(conn, tenant_id):
    with conn.cursor() as cur:
        cur.execute("SELECT versiune FROM public.supervizor_sursa WHERE tenant_id = %s",
                    (tenant_id,))
        r = cur.fetchone()
    return r[0] if r else 0


def scrie_rezultat(conn, tenant_id, an, luna, rezultat, versiune):
    """O singură instrucțiune (`INSERT … ON CONFLICT`): rezultatul e o valoare, scrisă atomic.

    `versiune` se dă de apelant și e cea citită **înainte** de calcul — altfel un calcul lung ar
    ștampila o versiune apărută în timpul lui, iar rezultatul ar părea curent fără să fie."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.supervizor_rezultat "
            "  (tenant_id, an, luna, rezultat, versiune_sursa, calculat_la) "
            "VALUES (%s, %s, %s, %s::jsonb, %s, now()) "
            # upsert-ok: rezultatul unei firme pe o perioadă e o valoare DERIVATĂ, recalculabilă
            # oricând din sursă. A o suprascrie cu una mai nouă e chiar scopul; nu e o intrare de
            # utilizator care s-ar pierde. Cheia (tenant_id, an, luna) e naturală.
            "ON CONFLICT (tenant_id, an, luna) DO UPDATE "
            "SET rezultat = EXCLUDED.rezultat, versiune_sursa = EXCLUDED.versiune_sursa, "
            "    calculat_la = EXCLUDED.calculat_la",
            (tenant_id, an, luna, json.dumps(rezultat, ensure_ascii=False, default=str), versiune))


def citeste(conn, tenant_ids, an, luna):
    """**Calea de citire: O SINGURĂ interogare pentru tot portofoliul.**

    Întoarce `{tenant_id: {rezultat, stare, calculat_la, versiune_sursa, versiune_curenta}}`.
    `stare` se DERIVĂ din comparația celor două versiuni — nu e stocată.

    Firmele fără rezultat apar cu `stare = "lipseste"` și `rezultat = None`: **absența se declară**,
    nu se confundă cu „fără constatări"."""
    if not tenant_ids:
        return {}
    with conn.cursor() as cur:
        cur.execute(
            "SELECT t.id, r.rezultat, r.versiune_sursa, r.calculat_la, "
            "       COALESCE(s.versiune, 0) AS versiune_curenta "
            "  FROM unnest(%s::int[]) AS t(id) "
            "  LEFT JOIN public.supervizor_rezultat r "
            "         ON r.tenant_id = t.id AND r.an = %s AND r.luna = %s "
            "  LEFT JOIN public.supervizor_sursa s ON s.tenant_id = t.id",
            (list(tenant_ids), an, luna))
        randuri = cur.fetchall()

    out = {}
    for tid, rez, v_calc, calculat_la, v_acum in randuri:
        if rez is None:
            out[tid] = {"rezultat": None, "stare": LIPSESTE, "calculat_la": None,
                        "versiune_sursa": None, "versiune_curenta": v_acum}
            continue
        stare = CURENT if v_calc == v_acum else INVALIDAT
        out[tid] = {"rezultat": rez, "stare": stare, "calculat_la": calculat_la,
                    "versiune_sursa": v_calc, "versiune_curenta": v_acum}
    return out


#: Mărimea LOTULUI de recalculare — nu e o valoare fiscală, e cât ia lucrătorul
#: dintr-o tură ca să nu țină conexiunea ocupată. Se schimbă fără temei legal.
LOT_RECALCULARE = 200


def de_recalculat(conn, an, luna, limita=LOT_RECALCULARE):
    """Firmele al căror rezultat nu mai e curent — pentru lucrătorul asincron.

    Include și firmele care n-au niciun rezultat. Ordonate după cât de veche e invalidarea, ca o
    firmă foarte activă să nu ție locul uneia care așteaptă de mult."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT s.tenant_id "
            "  FROM public.supervizor_sursa s "
            "  LEFT JOIN public.supervizor_rezultat r "
            "         ON r.tenant_id = s.tenant_id AND r.an = %s AND r.luna = %s "
            " WHERE r.tenant_id IS NULL OR r.versiune_sursa <> s.versiune "
            " ORDER BY s.schimbat_la ASC LIMIT %s",
            (an, luna, limita))
        return [r[0] for r in cur.fetchall()]

# ============================================================================
#  RECALCULAREA — per firmă, declanșată de invalidare, niciodată de o citire
# ============================================================================
def recalculeaza_firma(tenant_id, schema, an, luna, deschide=None):
    """Calculează rezultatul unei firme și îl persistă. `(stare, detaliu)`.

    **VERSIUNEA SE CITEȘTE ÎNAINTE DE CALCUL.** Dacă s-ar citi după, un calcul care durează ar
    ștampila o versiune apărută *în timpul lui*, iar rezultatul ar apărea `curent` deși descrie
    date de dinaintea ultimei scrieri. Citind-o înainte, cel mai rău caz e o invalidare în plus —
    firma se recalculează încă o dată. *Eroarea se împinge în direcția „mai multă muncă", nu în
    direcția „minte".*

    O firmă care ridică NU dispare și NU lasă rezultatul vechi drept curent: se scrie un rezultat
    care poartă chiar eroarea, cu aceeași versiune, deci starea rămâne onestă.
    """
    from core import db as _db, supervizor as _sv
    deschide = deschide or _db.get_conn

    with _db.get_conn() as c:
        v = versiune_sursa(c, tenant_id)

    try:
        with deschide(schema) as c:
            constatari, rulat, cauza = _sv._culege_firma(c, schema, an, luna)
    except Exception as e:      # noqa: BLE001 — orice eroare devine rezultat DECLARAT, nu tăcere
        # AFIRMAȚIE TIPATĂ, nu un dicționar propriu: `_neverificat` produce forma din nomenclatorul
        # închis al casei (`afirmatii.afirmatie`). O a doua formă a aceleiași propoziții ar fi
        # trecut pe lângă `test_afirmatii_tipate` și ar fi ajuns pe ecran altfel decât restul.
        rez = {"tenant_id": tenant_id, "constatari": [], "de_confirmat": 0,
               "rezultat": _sv.NEVERIFICAT,
               "neverificat": _sv._neverificat({"schema": schema}, "%s: %s" % (type(e).__name__, e),
                                               _sv.EXCEPTIE)}
        with _db.get_conn() as c:
            scrie_rezultat(c, tenant_id, an, luna, rez, v)
            c.commit()
        return "neverificat", rez["neverificat"]["eroare"]

    rez = {"tenant_id": tenant_id, "constatari": constatari,
           "de_confirmat": sum(1 for c in constatari if c.get("cere_confirmare")),
           "rezultat": (_sv.CONSTATARI if constatari else _sv.FARA_SUBIECT) if rulat
                       else _sv.NEVERIFICAT,
           "neverificat": None if rulat else _sv._neverificat({"schema": schema}, cauza,
                                                               _sv.AXA_NU_A_RULAT)}
    with _db.get_conn() as c:
        scrie_rezultat(c, tenant_id, an, luna, rez, v)
        c.commit()
    return "ok", len(constatari)


def recalculeaza_lot(an, luna, limita=LOT_RECALCULARE):
    """Lucrătorul: ia firmele invalidate și le recalculează. Pentru cron / rulare la nevoie.

    **NU rulează la citire.** Asta e chiar cerința: recalcularea se declanșează când se schimbă o
    dată sursă, nu la fiecare cerere și nu pentru tot portofoliul deodată."""
    from core import db as _db
    with _db.get_conn() as c:
        ids = de_recalculat(c, an, luna, limita)
        with c.cursor() as cur:
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE id = ANY(%s)", (ids,))
            scheme = dict(cur.fetchall())
    facute, sarite = 0, []
    for tid in ids:
        schema = scheme.get(tid)
        if not schema:
            sarite.append(tid)      # contor fără firmă (probă, firmă ștearsă) — se raportează
            continue
        recalculeaza_firma(tid, schema, an, luna)
        facute += 1
    return {"invalidate": len(ids), "recalculate": facute, "fara_firma": sarite}
