# -*- coding: utf-8 -*-
"""core/firma_rezumat.py — MODELUL DE CITIRE al portofoliului: un rând per firmă și aspect.

**DE CE EXISTĂ.** P2: *„numărul de interogări pentru o cerere de portofoliu nu crește proporțional cu
numărul de firme"*. Măsurat pe cele cinci rute, la 1000 de firme (curba 100/250/500/1000, creștere
liniară confirmată, ~2,0× la fiecare dublare):

| ruta | interogări | conexiuni | secunde |
|---|---|---|---|
| `migrare/solduri` | 4.000 | 2.001 | 1,24 |
| `migrare/plan-conturi` | 3.000 | 2.001 | 0,98 |
| `migrare/vector` | 3.000 | 2.001 | 1,01 |
| `termene` | 8.000 | 3.001 | 12,88 |
| **`control-fiscal`** | **278.882** | **12.001** | **70,81** |

**CE FACE MODULUL ĂSTA.** Ține, în `public`, câte un rând per (firmă, aspect), cu prospețimea
**derivată** din comparație — niciodată stocată. Citirea întregului portofoliu, pentru toate
aspectele, e **o singură interogare**.

═══════════════════════════════════════════════════════════════════════════════════════════════
 REMEDIEREA P2 (08.09.2026) — ce s-a schimbat față de prima formă, și de ce
═══════════════════════════════════════════════════════════════════════════════════════════════

Prima formă a trecut criteriul de acceptare (interogări constante) și **tot era greșită**, în patru
feluri deodată. Toate patru au aceeași rădăcină: *lista de dependențe a fost SCRISĂ, nu măsurată.*

**(1) UN SINGUR CONTOR PER FIRMĂ → invalidare grosolană.** Toate aspectele atârnau de
`supervizor_sursa.versiune`, un contor per firmă. O factură nouă invalida `tip_firma`. Prețul nu era
doar munca în plus: la 5 minute per tură, o firmă activă putea sta permanent invalidată pe TOATE
aspectele, adică permanent gri pe ecran.
*Acum:* contor per **(firmă, tabel)** în `firma_sursa_versiune`, iar versiunea unui aspect e suma
peste **tabelele lui**. O sursă invalidează exact ce depinde de ea. Citirea rămâne o interogare.

**(2) DEPENDENȚELE ERAU INCOMPLETE — 8 tabele din 27.** `scripts/scan_dependente.py` a măsurat ce
citește fiecare aspect (planul lui PostgreSQL + contoarele de scanare, confruntate). Aspectele
grele nu declarau **niciun** tabel; `control_fiscal` citește 27. Douăzeci de tabele scriau fără să
invalideze nimic — o valoare veche rămânea `curent`, tăcut, la nesfârșit. *Asta nu e supra-invalidare,
e SUB-invalidare, adică exact interdicția pe care modulul o poartă în antet.*
Lista se ține acum în `ASPECTE`, iar `core/test_dependente_masurate.py` o confruntă cu măsurătoarea.

**(3) TIMPUL NU ERA O DEPENDENȚĂ.** `termene` și `control_fiscal` primesc `azi` ca argument: verdictul
lor e „la termen / întârziat" **relativ la ziua de azi**. Un rezultat calculat ieri descrie ieri. Fără
nicio scriere în bază, la miezul nopții el devine fals — și, cum nicio versiune nu se schimbase,
se arăta `curent`. *O valoare care a încetat să fie adevărată fiindcă s-a schimbat ziua e la fel de
veche ca una căreia i s-a schimbat sursa.*
*Acum:* fiecare aspect declară `timp` (`"zi"`, `"luna"` sau `None`), rândul poartă `epoca` pentru
care a fost calculat, iar prospețimea cere **și** potrivirea epocii.

**(4) O EROARE DE CALCUL SE DĂDEA DREPT REZULTAT CURENT.** Calculul care ridica scria un dicționar
`{"eroare": ...}` cu versiunea curentă — deci `stare = curent`, iar apelantul trebuia să-și amintească
să se uite după cheia `eroare`. `/control-fiscal` își amintea; `de_recalculat` nu, deci firma nu mai
era niciodată reîncercată.
*Acum:* `stare_calcul` e o coloană proprie, iar citirea întoarce starea `eroare`, distinctă. Cu
reîncercare și pas crescător (`urmatoarea_incercare`), ca o eroare trecătoare să nu devină definitivă.

**INTERDICȚIA, neschimbată și nerelaxată:** o valoare veche NU se arată ca fiind curentă. Citirea
întoarce `stare ∈ {curent, invalidat, eroare, lipseste}` plus `calculat_la`. *O stare „în recalculare"
declarată e acceptabilă; una veche și tăcută nu e.*

**CE NU REZOLVĂ, declarat.** Modelul mută costul din citire în scriere; nu-l desființează. O firmă
care se schimbă des se recalculează des. Ce se câștigă e că **cererea interactivă nu mai plătește
pentru portofoliu** — plătește o dată, per firmă, per schimbare.
"""
from __future__ import annotations

import json

from core import cron as _cron

CURENT, INVALIDAT, LIPSESTE, EROARE = "curent", "invalidat", "lipseste", "eroare"

#: Stările de calcul stocate. `stare_calcul` NU e prospețimea (aia se derivă) — e ce s-a întâmplat
#: la ultima încercare de a produce valoarea.
CALCUL_OK, CALCUL_EROARE = "ok", "eroare"


def _solduri(conn, schema):
    from core import solduri_api
    r = solduri_api.rezumat(conn)
    return {"are_solduri": r["are_solduri"], "randuri": r["randuri"]}


def _plan_conturi(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM plan_conturi")
        return {"conturi": cur.fetchone()[0]}


def _vector(conn, schema):
    """Cheamă `vector_fiscal_api.citeste` — ACEEAȘI funcție pe care o chema ruta.

    Prima formă a acestui aspect făcea o interogare proprie pe `firma_profil` și inventa un câmp
    `complet`; ruta citea `completat`, din altă funcție. *Două definiții ale aceleiași stări sunt
    începutul unei divergențe tăcute* — și e chiar clasa reparată la R94."""
    from core import vector_fiscal_api
    v = vector_fiscal_api.citeste(conn) or {}
    return {"completat": bool(v.get("completat")), "regim_fiscal": v.get("regim_fiscal"),
            "platitor_tva": v.get("platitor_tva"), "tip_decont": v.get("tip_decont"),
            "operatiuni_ic": v.get("operatiuni_ic")}


def _parteneri(conn, schema):
    """[P3 val B] `solduri_parteneri_api.rezumat` — ACEEAȘI funcție pe care o chema ruta.

    Ea cheamă `asigura_tabel(conn)`, adică DDL. Se păstrează: ruta face exact asta azi, iar
    aspectul n-are voie să răspundă altceva decât răspundea ecranul. *DDL-ul e nevinovat câtă
    vreme conexiunea are `search_path` pe schema firmei* — când n-a avut, tabela a aterizat în
    `public` (incidentul din diagnosticul P3, `masuratori/post_p2/p3_searchpath_failure_mode.txt`).
    Lucrătorul deschide `db.get_conn(schema)`, deci o are."""
    from core import solduri_parteneri_api
    r = solduri_parteneri_api.rezumat(conn)
    return {"are_parteneri": r["are_parteneri"], "randuri": r["randuri"]}


def _salariati(conn, schema):
    """[P3 val B] Cheamă `salariati_import_api.rezumat`, ca ruta."""
    from core import salariati_import_api
    r = salariati_import_api.rezumat(conn)
    return {"are_salariati": r["are_salariati"], "randuri": r["randuri"]}


def _asociati(conn, schema):
    """[P3 val B] Cheamă `asociati_import_api.rezumat`, ca ruta."""
    from core import asociati_import_api
    r = asociati_import_api.rezumat(conn)
    return {"are_asociati": r["are_asociati"], "randuri": r["randuri"]}


def _mijloace_fixe(conn, schema):
    """[P3 val B] Cheamă `mijloace_fixe_import_api.rezumat`, ca ruta."""
    from core import mijloace_fixe_import_api
    r = mijloace_fixe_import_api.rezumat(conn)
    return {"are_mijloace": r["are_mijloace"], "randuri": r["randuri"]}


# ============================================================================
#  REGISTRUL ASPECTELOR — `tabele` sunt MĂSURATE, nu scrise
# ============================================================================
#: Fiecare aspect poartă:
#:   * `tabele`        — tabelele-sursă din schema firmei. **Măsurate** cu `scripts/scan_dependente.py`
#:                       pe TOT portofoliul (reuniune peste firme: un scan pe o singură firmă vede
#:                       doar ramurile pe care datele ei le ating — `miscari_stoc` apare la 2 firme
#:                       din 20). Aici se pun triggerele, deci lista asta E mecanismul de invalidare.
#:   * `tabele_public` — sursele din `public`, per firmă. Nu pot purta trigger cu `tenant_id` fixat la
#:                       creare (rândurile lor sunt de mai multe firme), deci au trigger propriu care
#:                       citește `tenant_id` din rând.
#:   * `timp`          — granularitatea temporală a rezultatului: `None` = nu depinde de ceas;
#:                       `"zi"` = se învechește la schimbarea zilei; `"luna"` = a lunii.
#:   * `calcul`        — funcția care produce valoarea, chemată **exact ca azi**, ca să nu existe
#:                       două definiții ale aceleiași cifre. `None` la aspectele grele, care se
#:                       calculează împreună prin `recalculeaza_greu`.
#:
#: CE NU E AICI, și de ce: `public.tenants`, `public.users`, `public.accounting_firms` sunt citite
#: (rezolvarea numelui firmei și a contextului de acces), dar poartă DENUMIREA și cabinetul, nu
#: faptele din care iese verdictul. O redenumire de firmă n-are voie să invalideze 1000 de rezumate.
#: *Se scrie aici ca să fie o alegere, nu o omisiune.*
NEURMARITE_PUBLIC = ("tenants", "users", "accounting_firms")

_T_CONTROL_FISCAL = (
    "articole", "asociati", "beneficii_lunare", "bonuri", "casa_operatiuni", "chitante",
    "clienti", "concedii_medicale", "d300_manual", "d301_operatiuni", "d390_manual",
    "d390_reclasificare", "extras_linii", "factura_linii", "facturi", "firma_profil",
    "furnizori", "inregistrari", "inregistrari_linii", "mijloace_fixe", "miscari_stoc",
    "perioada_confirmata", "plan_conturi", "pontaj", "salariati", "salariu_istoric",
    "solduri_initiale")

_T_TERMENE = ("clienti", "d390_manual", "facturi", "firma_profil", "salariati")

ASPECTE = {
    "solduri": {
        "tabele": ("solduri_initiale",), "tabele_public": (), "timp": None,
        "calcul": _solduri},
    "plan_conturi": {
        "tabele": ("plan_conturi",), "tabele_public": (), "timp": None,
        "calcul": _plan_conturi},
    "vector": {
        "tabele": ("firma_profil",), "tabele_public": (), "timp": None,
        "calcul": _vector},
    # ── [P3 val B, 09.09.2026] cele patru straturi de migrare ──
    #
    # Rutele lor citeau firmă cu firmă, cu DOUĂ conexiuni fiecare (una ca să afle schema, una ca
    # s-o deschidă). Măsurat pe cererea HTTP întreagă, la 1000 de firme:
    #     /migrare/parteneri       4.004 interogări / 2.003 conexiuni  (q = 4 + 4N)
    #     /migrare/asociati        3.004 / 2.003                        (q = 4 + 3N)
    #     /migrare/mijloace-fixe   3.004 / 2.003                        (q = 4 + 3N)
    #     /migrare/salariati       3.004 / 2.003                        (q = 4 + 3N)
    #
    # Datele stau în schema FIECĂREI firme, nu în `public` cu `tenant_id` — deci nu există un
    # `GROUP BY` care să le adune, cum a fost la valul A. Un `UNION ALL` construit peste cele N
    # scheme ar fi dat o singură interogare pe o singură conexiune, adică panta 0 la litera
    # criteriului, dar textul și planul cresc cu N: latența ar fi crescut mai departe. *Un criteriu
    # trecut fără ca problema să fie rezolvată e cosmetică, nu remediere.*
    #
    # `timp: None` — niciuna nu depinde de ceas: sunt numărători de rânduri, nu scadențe.
    "parteneri": {
        "tabele": ("solduri_parteneri",), "tabele_public": (), "timp": None,
        "calcul": _parteneri},
    "salariati": {
        "tabele": ("salariati",), "tabele_public": (), "timp": None,
        "calcul": _salariati},
    "asociati": {
        "tabele": ("asociati",), "tabele_public": (), "timp": None,
        "calcul": _asociati},
    "mijloace_fixe": {
        "tabele": ("mijloace_fixe",), "tabele_public": (), "timp": None,
        "calcul": _mijloace_fixe},
    # ── grele: se calculează împreună, în `recalculeaza_greu` ──
    "termene": {
        "tabele": _T_TERMENE, "tabele_public": ("declaratii_depuse",),
        # ZI: fereastra de scadențe e „următoarele 60 de zile de la `azi`", iar eticheta fiecărei
        # scadențe („mai sunt 3 zile" / „a trecut termenul") se schimbă la miezul nopții fără ca
        # nimic din bază să se fi atins.
        "timp": "zi", "calcul": None},
    "control_fiscal": {
        "tabele": _T_CONTROL_FISCAL, "tabele_public": ("declaratii_depuse",),
        # ZI: `evalueaza_firma` primește `azi` și decide „lipsă / de urmărit / la termen" față de
        # termenele legale ale lunii curente. Ieri D300 nu era încă restantă; azi este.
        "timp": "zi", "calcul": None},
}

#: Aspectele care se produc printr-o singură trecere grea, împreună.
ASPECTE_GRELE = ("termene", "control_fiscal")
#: Aspectele ușoare — o conexiune la schema firmei, câteva interogări.
ASPECTE_USOARE = tuple(a for a in ASPECTE if ASPECTE[a]["calcul"] is not None)

TOATE = tuple(ASPECTE)

#: `tip_firma` NU MAI E UN ASPECT AL MODELULUI, și e o schimbare deliberată — vezi
#: `public.firma_tip` mai jos și `auth_api.tenantii_userului`. Ca aspect, el avea o fereastră în
#: care lipsea sau era învechit, iar `tenantii_userului` cădea pe calea veche, per firmă: bucla
#: O(N) pe care P2 tocmai o scosese se întorcea exact când modelul era rece. Fiind o PROIECȚIE
#: întreținută sincron de trigger, nu are fereastră deloc, deci nu mai are nevoie de cale de rezervă.
ASPECT_RETRAS_TIP_FIRMA = "tip_firma"


def tabele_urmarite():
    """Toate tabelele-sursă din schema firmei, ca mulțime. DERIVATĂ din registru, nu scrisă.

    Asta e lista pe care se pun triggerele. Include `firma_profil`, sursa lui `public.firma_tip`."""
    out = set()
    for a in ASPECTE.values():
        out |= set(a["tabele"])
    return sorted(out)


def tabele_publice_urmarite():
    out = set()
    for a in ASPECTE.values():
        out |= set(a["tabele_public"])
    return sorted(out)


def tabele_cu_trigger():
    """Tabelele pe care se pune trigger — REUNIUNEA surselor modelului cu cele ale supervizorului.

    Nu e același lucru cu `tabele_urmarite()`: `efactura_trimiteri` nu e sursă pentru niciun aspect
    al modelului, dar e sursă pentru supervizor (P1). O singură funcție de trigger le servește pe
    amândouă, deci un tabel are un singur trigger indiferent câți consumatori are. *Două triggere
    pe același tabel ar fi două mecanisme care pot diverge.*"""
    from core import supervizor_cache as _sc
    return sorted(set(tabele_urmarite()) | set(_sc.TABELE_TENANT))


def aspecte_ale_tabelei(tabela):
    """Ce aspecte invalidează o scriere în `tabela`. Inversa registrului — folosită de gărzi."""
    return sorted(a for a, d in ASPECTE.items()
                  if tabela in d["tabele"] or tabela in d["tabele_public"])


def epoca_pentru(aspect, azi):
    """Eticheta de timp pentru care e valabil un rezultat. `''` = nu depinde de ceas.

    E un ȘIR, nu o dată, fiindcă e o CHEIE de egalitate, nu o valoare de comparat: prospețimea
    întreabă „e aceeași epocă?", nu „e mai nouă?"."""
    t = ASPECTE.get(aspect, {}).get("timp")
    if t == "zi":
        return azi.strftime("%Y-%m-%d")
    if t == "luna":
        return azi.strftime("%Y-%m")
    return ""


# ============================================================================
#  SCHEMA
# ============================================================================
DDL = """
-- CONTORUL, per (firmă, TABEL). Prima formă avea un contor per firmă, deci orice scriere
-- invalida orice aspect. Aici, versiunea unui aspect e suma peste tabelele LUI.
-- INVARIANTA, si e cea pe care sta tot modelul de prospetime:
--   `versiune` e MONOTON CRESCATOARE pentru fiecare pereche (tenant_id, tabela).
-- Prospetimea se decide comparand suma contoarelor de acum cu suma de la calcul. Daca un
-- contor ar putea SCADEA, o suma veche ar putea redeveni egala cu cea curenta — iar un rezumat
-- invechit ar reaparea ca `curent`, tacut. *Nu e o preferinta de proiectare: e chiar conditia
-- in care comparatia de versiuni inseamna ceva.* Impusa mai jos de `versiune_doar_creste`.
CREATE TABLE IF NOT EXISTS public.firma_sursa_versiune (
    tenant_id    integer     NOT NULL,
    tabela       text        NOT NULL,
    versiune     bigint      NOT NULL DEFAULT 1,
    schimbat_la  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, tabela)
);
CREATE INDEX IF NOT EXISTS ix_firma_sursa_versiune_tabela
    ON public.firma_sursa_versiune (tabela);

-- MAPAREA aspect -> tabelă, PROIECTATĂ din `ASPECTE` la pornire. Trăiește în bază fiindcă
-- agregarea versiunii per aspect se face în SQL, într-o singură interogare; a o trimite ca
-- parametru la fiecare citire ar muta registrul în apelant, unde s-ar putea desincroniza.
CREATE TABLE IF NOT EXISTS public.firma_aspect_sursa (
    aspect  text NOT NULL,
    tabela  text NOT NULL,
    PRIMARY KEY (aspect, tabela)
);

-- Care tabele contează pentru contorul AGREGAT al supervizorului (P1). Ține în bază ce declară
-- `supervizor_cache.TABELE_TENANT`, ca funcția de trigger să nu poarte o a doua copie a listei.
CREATE TABLE IF NOT EXISTS public.sursa_supervizor (
    tabela text PRIMARY KEY
);

-- PROIECȚIA `tip_firma`, întreținută SINCRON de trigger. Vezi `ASPECT_RETRAS_TIP_FIRMA`.
CREATE TABLE IF NOT EXISTS public.firma_tip (
    tenant_id     integer PRIMARY KEY,
    tip_firma     text,
    actualizat_la timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.firma_rezumat (
    tenant_id      integer     NOT NULL,
    aspect         text        NOT NULL,
    date           jsonb       NOT NULL,
    versiune_sursa bigint      NOT NULL,
    calculat_la    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, aspect)
);

-- Coloanele adăugate la remediere. `ADD COLUMN IF NOT EXISTS` ca migrarea să fie idempotentă
-- și să nu ceară o bază goală.
ALTER TABLE public.firma_rezumat ADD COLUMN IF NOT EXISTS epoca text NOT NULL DEFAULT '';
ALTER TABLE public.firma_rezumat ADD COLUMN IF NOT EXISTS stare_calcul text NOT NULL DEFAULT 'ok';
ALTER TABLE public.firma_rezumat ADD COLUMN IF NOT EXISTS incercari integer NOT NULL DEFAULT 0;
ALTER TABLE public.firma_rezumat ADD COLUMN IF NOT EXISTS urmatoarea_incercare timestamptz;
"""

#: Funcțiile de trigger. Separate de DDL fiindcă se rescriu la fiecare pornire (`CREATE OR REPLACE`),
#: iar corpul lor derivă din tabelele de mapare de mai sus, nu din liste repetate în SQL.
DDL_FUNCTII = """
-- Contorul se ridică la SCRIERE. `tenant_id` vine ca argument de trigger, fixat la creare:
-- triggerul rulează în schema firmei, unde `tenant_id` nu e o coloană a fiecărui tabel.
CREATE OR REPLACE FUNCTION public.marcheaza_sursa() RETURNS trigger AS $$
DECLARE tid integer := TG_ARGV[0]::integer;
BEGIN
    -- upsert-ok: contorul E o valoare care se suprascrie prin definiție — fiecare scriere în
    -- sursă îl incrementează. Nu există „date ale utilizatorului" de pierdut aici.
    INSERT INTO public.firma_sursa_versiune (tenant_id, tabela, versiune, schimbat_la)
         VALUES (tid, TG_TABLE_NAME, 1, now())
    ON CONFLICT (tenant_id, tabela) DO UPDATE
            SET versiune = public.firma_sursa_versiune.versiune + 1, schimbat_la = now();

    -- Contorul AGREGAT al supervizorului (P1) rămâne cum era, ca să nu se schimbe purtarea unui
    -- consumator deja gardat. Ce tabele intră în el e o INTEROGARE, nu o listă repetată aici.
    IF EXISTS (SELECT 1 FROM public.sursa_supervizor WHERE tabela = TG_TABLE_NAME) THEN
        INSERT INTO public.supervizor_sursa (tenant_id, versiune, schimbat_la)
             VALUES (tid, 1, now())
        -- upsert-ok: același contor, aceeași justificare.
        ON CONFLICT (tenant_id) DO UPDATE
                SET versiune = public.supervizor_sursa.versiune + 1, schimbat_la = now();
    END IF;
    RETURN NULL;   -- AFTER trigger: valoarea întoarsă e ignorată
END;
$$ LANGUAGE plpgsql;

-- PROIECȚIA `tip_firma`. Rulează pe `firma_profil`, deci vede valoarea; al doilea argument e
-- schema, fiindcă triggerul e STATEMENT-level și trebuie să RECITEASCĂ rândul (nu are NEW).
CREATE OR REPLACE FUNCTION public.proiecteaza_tip_firma() RETURNS trigger AS $$
DECLARE tid integer := TG_ARGV[0]::integer;
        sch text    := TG_ARGV[1];
        val text;
BEGIN
    EXECUTE format('SELECT tip_firma FROM %I.firma_profil WHERE id = 1', sch) INTO val;
    -- upsert-ok: proiecție DERIVATĂ dintr-o singură sursă; a o suprascrie e chiar scopul.
    INSERT INTO public.firma_tip (tenant_id, tip_firma, actualizat_la)
         VALUES (tid, val, now())
    ON CONFLICT (tenant_id) DO UPDATE
            SET tip_firma = EXCLUDED.tip_firma, actualizat_la = now();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- PAZNICUL INVARIANTEI. Respinge orice scadere a contorului, indiferent cine scrie — calea
-- aplicatiei, o migrare externa sau o mana pe `psql`. Costa un apel de functie per actualizare de
-- contor; contorul se actualizeaza oricum la fiecare scriere in sursa, deci pretul e marginal, iar
-- ce cumpara e ca invarianta nu mai depinde de disciplina apelantilor.
CREATE OR REPLACE FUNCTION public.versiune_doar_creste() RETURNS trigger AS $$
BEGIN
    IF NEW.versiune < OLD.versiune THEN
        RAISE EXCEPTION
            'firma_sursa_versiune.versiune nu poate scadea (firma %, tabela %): % -> %. '
            'Prospetimea modelului de citire se decide pe comparatia de versiuni; un contor care '
            'scade ar face un rezumat invechit sa reapara drept curent.',
            OLD.tenant_id, OLD.tabela, OLD.versiune, NEW.versiune
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Sursele din `public` sunt ale MAI MULTOR firme, deci `tenant_id` nu se poate fixa la creare:
-- se citește din rând. ROW-level, fiindcă exact rândul spune despre ce firmă e vorba.
CREATE OR REPLACE FUNCTION public.marcheaza_sursa_publica() RETURNS trigger AS $$
DECLARE tid integer;
BEGIN
    tid := COALESCE((to_jsonb(NEW) ->> 'tenant_id')::integer,
                    (to_jsonb(OLD) ->> 'tenant_id')::integer);
    IF tid IS NULL THEN
        RETURN NULL;
    END IF;
    INSERT INTO public.firma_sursa_versiune (tenant_id, tabela, versiune, schimbat_la)
         VALUES (tid, TG_TABLE_NAME, 1, now())
    -- upsert-ok: contor.
    ON CONFLICT (tenant_id, tabela) DO UPDATE
            SET versiune = public.firma_sursa_versiune.versiune + 1, schimbat_la = now();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""


def aplica_ddl(conn):
    """Tabelele + funcțiile de trigger + proiecția registrului. Idempotent.

    **Se cheamă din `lifespan()`.** Prima formă nu era chemată de nicăieri: tabela exista pe server
    doar fiindcă o rulasem de mână în timpul măsurătorilor. Pe o bază proaspătă, tot P2 ar fi căzut
    pe ramura „modelul lipsește" — tăcut, fiindcă `tenantii_userului` prinde excepția."""
    from core import supervizor_cache as _sc
    with conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute(DDL_FUNCTII)
        # paznicul monotoniei, legat de tabela contoarelor (idempotent)
        cur.execute("DROP TRIGGER IF EXISTS trg_versiune_doar_creste "
                    "  ON public.firma_sursa_versiune")
        cur.execute("CREATE TRIGGER trg_versiune_doar_creste "
                    "BEFORE UPDATE ON public.firma_sursa_versiune "
                    "FOR EACH ROW EXECUTE FUNCTION public.versiune_doar_creste()")
        # Registrul, PROIECTAT din cod. Se șterge și se rescrie: dacă un aspect pierde o sursă,
        # rândul vechi ar continua să-l invalideze, iar aspectul s-ar recalcula la nesfârșit.
        cur.execute("DELETE FROM public.firma_aspect_sursa")
        perechi = []
        for a, d in ASPECTE.items():
            for t in tuple(d["tabele"]) + tuple(d["tabele_public"]):
                perechi.append((a, t))
        cur.executemany("INSERT INTO public.firma_aspect_sursa (aspect, tabela) VALUES (%s, %s)",
                        perechi)
        cur.execute("DELETE FROM public.sursa_supervizor")
        cur.executemany("INSERT INTO public.sursa_supervizor (tabela) VALUES (%s)",
                        [(t,) for t in _sc.TABELE_TENANT])


# ============================================================================
#  TRIGGERE — se leagă la pornire, pentru TOATE firmele, și la crearea uneia noi
# ============================================================================
def leaga_triggerele_firma(conn, schema, tenant_id):
    """Pune triggerele pe tabelele-sursă ale unei firme. Idempotent (DROP … IF EXISTS, apoi CREATE).

    STATEMENT-level, nu ROW: contorul trebuie să crească o dată per scriere, nu o dată per rând —
    un import de 5.000 de facturi n-are de ce să ridice contorul de 5.000 de ori.

    Întoarce câte triggere a pus, ca migrarea să poată fi VERIFICATĂ, nu doar rulată."""
    from core import db as _db
    if not _db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    puse = 0
    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.firma_sursa_versiune (tenant_id, tabela) "
                    "VALUES (%s, '__firma__') ON CONFLICT DO NOTHING", (tenant_id,))
        for t in tabele_cu_trigger():
            cur.execute("SELECT to_regclass(%s)", ("%s.%s" % (schema, t),))
            if cur.fetchone()[0] is None:
                continue                       # tabelul nu există în schema asta — nu se inventează
            nume = "trg_sursa_%s" % t
            cur.execute('DROP TRIGGER IF EXISTS %s ON "%s".%s' % (nume, schema, t))
            cur.execute(
                'CREATE TRIGGER %s AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON "%s".%s '
                "FOR EACH STATEMENT EXECUTE FUNCTION public.marcheaza_sursa(%d)"
                % (nume, schema, t, tenant_id))
            puse += 1
            # vechiul trigger al supervizorului pe același tabel ar dubla contorul lui
            cur.execute('DROP TRIGGER IF EXISTS trg_supervizor_%s ON "%s".%s' % (t, schema, t))
        # proiecția `tip_firma`, pe firma_profil
        cur.execute("SELECT to_regclass(%s)", ("%s.firma_profil" % schema,))
        if cur.fetchone()[0] is not None:
            cur.execute('DROP TRIGGER IF EXISTS trg_tip_firma ON "%s".firma_profil' % schema)
            cur.execute(
                'CREATE TRIGGER trg_tip_firma AFTER INSERT OR UPDATE OR DELETE ON "%s".firma_profil '
                "FOR EACH STATEMENT EXECUTE FUNCTION public.proiecteaza_tip_firma(%d, %s)"
                % (schema, tenant_id, _literal(schema)))
            puse += 1
            # SĂMÂNȚA proiecției: fără ea, o firmă în care nu s-a mai scris de la migrare n-ar avea
            # rând în `firma_tip`, iar lista portofoliului ar arăta un `tip_firma` gol pentru ea.
            # SĂMÂNȚA proiecției. Numele schemei se interpolează (nu poate fi parametru), dar a
            # trecut deja prin `schema_valida` la intrarea în funcție; `tenant_id` rămâne parametru.
            cur.execute(
                'INSERT INTO public.firma_tip (tenant_id, tip_firma, actualizat_la) '
                'SELECT %%s, tip_firma, now() FROM "%s".firma_profil WHERE id = 1 '
                # upsert-ok: proiecție derivată, v. funcția de trigger.
                'ON CONFLICT (tenant_id) DO UPDATE SET tip_firma = EXCLUDED.tip_firma, '
                '    actualizat_la = now()' % schema, (tenant_id,))
    return puse


def _literal(s):
    return "'" + s.replace("'", "''") + "'"


def leaga_triggerele_publice(conn):
    """Triggerele pe sursele din `public`. O dată per bază, nu per firmă."""
    puse = 0
    with conn.cursor() as cur:
        for t in tabele_publice_urmarite():
            cur.execute("SELECT to_regclass(%s)", ("public.%s" % t,))
            if cur.fetchone()[0] is None:
                continue
            nume = "trg_sursa_pub_%s" % t
            cur.execute("DROP TRIGGER IF EXISTS %s ON public.%s" % (nume, t))
            cur.execute(
                "CREATE TRIGGER %s AFTER INSERT OR UPDATE OR DELETE ON public.%s "
                "FOR EACH ROW EXECUTE FUNCTION public.marcheaza_sursa_publica()" % (nume, t))
            puse += 1
    return puse


def migreaza_triggerele(conn, doar_active=True):
    """Leagă triggerele pe TOȚI tenanții existenți. Idempotentă, verificabilă.

    **DE CE EXISTĂ.** `leaga_triggerele` din prima formă nu era chemată din niciun loc din cod —
    zero apeluri. Triggerele existau pe server fiindcă le pusesem de mână în timpul unei sesiuni.
    O bază refăcută din dump, sau o firmă nouă, n-ar fi avut niciunul: modelul s-ar fi calculat o
    dată și ar fi rămas `curent` pe veci, fiindcă nimic nu i-ar mai fi ridicat contorul.
    *O migrare care trăiește doar în istoricul unei sesiuni nu e o migrare.*"""
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants "
                    "WHERE (%s = false OR activ) ORDER BY id", (doar_active,))
        firme = cur.fetchall()
    raport = {"firme": 0, "triggere": 0, "esecuri": []}
    raport["triggere_publice"] = leaga_triggerele_publice(conn)
    for tid, schema in firme:
        # ── FIECARE FIRMĂ, ÎNTR-UN SAVEPOINT AL EI ────────────────────────────────
        # Fără el, prima eroare SQL lasă tranzacția în `current transaction is aborted`, iar
        # TOATE firmele următoare pică din cauza asta — nu din cauza lor. Raportul ar fi spus
        # „19 firme rupte" despre o singură firmă ruptă, iar diagnosticul ar fi trimis omul să
        # caute în locul greșit. *Siguranța nu se schimbă: orice eșec tot oprește pornirea.
        # Ce se schimbă e că raportul numește CAUZA REALĂ, per firmă.*
        with conn.cursor() as cur:
            cur.execute("SAVEPOINT p2_tenant")
        try:
            raport["triggere"] += leaga_triggerele_firma(conn, schema, tid)
            with conn.cursor() as cur:
                cur.execute("RELEASE SAVEPOINT p2_tenant")
            raport["firme"] += 1
        except Exception as e:      # noqa: BLE001 — o firmă care nu se poate lega nu oprește
            # BUCLA (celelalte firme se încearcă și ele, ca raportul să spună CÂTE sunt rupte, nu
            # doar prima). Ce face APELANTUL cu raportul e altceva: `lifespan()` nu are voie să
            # continue peste el — vezi `main.py`, blocul de infrastructură critică.
            import traceback as _tb
            with conn.cursor() as cur:
                cur.execute("ROLLBACK TO SAVEPOINT p2_tenant")
                cur.execute("RELEASE SAVEPOINT p2_tenant")
            raport["esecuri"].append({
                "tenant_id": tid, "schema": schema,
                "exceptie": "%s: %s" % (type(e).__name__, e),
                "traceback": _tb.format_exc()})
    return raport


#: Ce trebuie să existe ca `citeste()` să poată decide corect prospețimea. Lista NU e o
#: convenienta: fiecare intrare e o piesa fara de care o valoare veche s-ar putea arata `curent`.
TABELE_CENTRALE = ("firma_rezumat", "firma_sursa_versiune", "firma_aspect_sursa",
                   "sursa_supervizor", "firma_tip", "supervizor_sursa")
#: Coloanele adaugate la remediere. Lipsa lor nu da eroare de sintaxa la citire — da o citire care
#: nu mai stie de epoca sau de starea de calcul, adica exact clasa reparata.
COLOANE_REZUMAT = ("epoca", "stare_calcul", "incercari", "urmatoarea_incercare")
#: Functiile PostgreSQL fara de care triggerele exista dar nu fac nimic.
FUNCTII_PG = ("marcheaza_sursa", "proiecteaza_tip_firma", "marcheaza_sursa_publica",
              "versiune_doar_creste")

#: NOMENCLATORUL INCHIS al problemelor de infrastructura. Codurile sunt pentru apelanti (gardă,
#: healthcheck, log structurat), mesajele pentru oameni. Stau aici, intr-un singur loc, ca o probă
#: care asertează pe un cod să nu-l poarte ca literal — un literal repetat e a doua definiție a
#: aceleiași propoziții, și prima care rămâne în urmă.
COD_TABELE_LIPSA = "TABELE_LIPSA"
COD_COLOANE_LIPSA = "COLOANE_LIPSA"
COD_FUNCTII_LIPSA = "FUNCTII_LIPSA"
COD_REGISTRU_DESINCRONIZAT = "REGISTRU_DESINCRONIZAT"
COD_TRIGGERE_LIPSA = "TRIGGERE_LIPSA"
COD_PROIECTII_LIPSA = "PROIECTII_LIPSA"
COD_TRIGGERE_PUBLICE_LIPSA = "TRIGGERE_PUBLICE_LIPSA"
CODURI_INFRASTRUCTURA = (COD_TABELE_LIPSA, COD_COLOANE_LIPSA, COD_FUNCTII_LIPSA,
                         COD_REGISTRU_DESINCRONIZAT, COD_TRIGGERE_LIPSA, COD_PROIECTII_LIPSA,
                         COD_TRIGGERE_PUBLICE_LIPSA)


def verifica_infrastructura(conn):
    """`{ok, probleme, detaliu}` — TOATĂ infrastructura P2, nu doar triggerele.

    Fiecare problemă e un dicționar cu `cod` (nomenclator închis), `ce` (datele) și `diagnostic`
    (proza). **Codul e pentru apelanți, proza pentru omul care ridică serverul** — un apelant care
    ar căuta un subșir în proză s-ar rupe tăcut la prima rescriere a ei.

    Cheia se numește `diagnostic`, nu `mesaj`, și nu e o preferință de stil: în casă `mesaj` e
    cheia unui text ARĂTAT CONTABILULUI, iar gărzile o tratează ca atare — nume interne de câmp
    interzise (`test_mesaje_fara_camp_intern`), afirmații tipate obligatorii
    (`test_afirmatii_tipate`). Problemele de aici nu ajung pe niciun ecran: numesc tabele, coloane
    și funcții PostgreSQL, pentru cine pornește procesul. *Un diagnostic de infrastructură scris în
    vocabularul mesajelor de utilizator ar fi fost obligat să nu-și numească propriul subiect.*

    **DE CE E MAI MULT DECÂT `verifica_triggerele`.** Un `CREATE TRIGGER` care n-a ridicat excepție
    nu spune că mecanismul funcționează: triggerul poate exista peste o funcție care lipsește,
    registrul `firma_aspect_sursa` poate fi gol (și atunci versiunea oricărui aspect e 0, deci
    orice rezumat pare curent la infinit), iar coloana `epoca` poate lipsi (și atunci dependența de
    timp dispare tăcut). *Fiecare dintre astea produce exact defectul pe care P2 îl repară — o
    valoare veche arătată drept curentă — și niciuna nu produce o eroare.*

    Se cheamă din `lifespan()`, iar rezultatul DECIDE dacă aplicația intră în `ready`."""
    probleme, detaliu = [], {}

    with conn.cursor() as cur:
        # (1) tabelele centrale
        lipsa_tab = []
        for t in TABELE_CENTRALE:
            cur.execute("SELECT to_regclass(%s)", ("public.%s" % t,))
            if cur.fetchone()[0] is None:
                lipsa_tab.append(t)
        detaliu["tabele_lipsa"] = lipsa_tab
        if lipsa_tab:
            probleme.append({"cod": COD_TABELE_LIPSA, "ce": lipsa_tab,
                             "diagnostic": "tabele centrale lipsă: %s" % ", ".join(lipsa_tab)})

        # (2) coloanele adăugate la remediere
        if "firma_rezumat" not in lipsa_tab:
            cur.execute("SELECT column_name FROM information_schema.columns "
                        " WHERE table_schema = 'public' AND table_name = 'firma_rezumat'")
            au = {r[0] for r in cur.fetchall()}
            lipsa_col = [c for c in COLOANE_REZUMAT if c not in au]
            detaliu["coloane_lipsa"] = lipsa_col
            if lipsa_col:
                probleme.append({"cod": COD_COLOANE_LIPSA, "ce": lipsa_col,
                                 "diagnostic": "coloane lipsă în `firma_rezumat`: %s"
                                          % ", ".join(lipsa_col)})

        # (3) funcțiile PostgreSQL
        cur.execute("SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
                    " WHERE n.nspname = 'public' AND p.proname = ANY(%s)", (list(FUNCTII_PG),))
        au_fn = {r[0] for r in cur.fetchall()}
        lipsa_fn = [f for f in FUNCTII_PG if f not in au_fn]
        detaliu["functii_lipsa"] = lipsa_fn
        if lipsa_fn:
            probleme.append({"cod": COD_FUNCTII_LIPSA, "ce": lipsa_fn,
                             "diagnostic": "funcții PostgreSQL lipsă: %s" % ", ".join(lipsa_fn)})

        # (4) registrul aspect->sursă, COMPARAT cu ce declară codul. Un registru care a rămas în
        #     urmă nu se vede: agregarea pur și simplu nu numără sursa lipsă.
        if "firma_aspect_sursa" not in lipsa_tab:
            cur.execute("SELECT aspect, tabela FROM public.firma_aspect_sursa")
            in_baza = {(a, t) for a, t in cur.fetchall()}
            in_cod = {(a, t) for a, d in ASPECTE.items()
                      for t in tuple(d["tabele"]) + tuple(d["tabele_public"])}
            detaliu["registru_in_baza"] = len(in_baza)
            detaliu["registru_in_cod"] = len(in_cod)
            if in_baza != in_cod:
                probleme.append({
                    "cod": COD_REGISTRU_DESINCRONIZAT,
                    "ce": {"doar_in_cod": sorted(in_cod - in_baza),
                           "doar_in_baza": sorted(in_baza - in_cod)},
                    "diagnostic": "registrul `firma_aspect_sursa` diferă de `ASPECTE`: %d perechi doar "
                             "în cod, %d doar în bază"
                             % (len(in_cod - in_baza), len(in_baza - in_cod))})

    # (5) triggerele, pe fiecare firmă activă
    trg = verifica_triggerele(conn)
    detaliu["firme_active"] = trg["firme_vazute"]
    detaliu["triggere_lipsa"] = trg["lipsa"]
    if trg["lipsa"]:
        probleme.append({"cod": COD_TRIGGERE_LIPSA, "ce": trg["lipsa"],
                         "diagnostic": "triggere lipsă pe %d perechi (firmă, tabel), primele: %s"
                                  % (len(trg["lipsa"]), trg["lipsa"][:5])})
    # ZERO firme NU e o problemă (bază proaspătă, fără tenanți), dar se SPUNE — altfel un „ok" pe
    # zero firme s-ar citi ca „toate firmele sunt în regulă".
    detaliu["domeniu_gol"] = trg["domeniu_gol"]
    if not trg["domeniu_gol"] and trg["proiectii_tip_firma"] < trg["firme_vazute"]:
        probleme.append({"cod": COD_PROIECTII_LIPSA,
                         "ce": {"proiectii": trg["proiectii_tip_firma"],
                                "firme": trg["firme_vazute"]},
                         "diagnostic": "proiecții `tip_firma`: %d pentru %d firme active — lista "
                                  "portofoliului ar arăta gol pentru unele"
                                  % (trg["proiectii_tip_firma"], trg["firme_vazute"])})

    # (6) triggerele pe sursele din `public`
    with conn.cursor() as cur:
        lipsa_pub = []
        for t in tabele_publice_urmarite():
            cur.execute("SELECT count(*) FROM pg_trigger tg JOIN pg_class cl ON cl.oid = tg.tgrelid "
                        "  JOIN pg_namespace n ON n.oid = cl.relnamespace "
                        " WHERE n.nspname = 'public' AND cl.relname = %s AND tg.tgname = %s "
                        "   AND NOT tg.tgisinternal", (t, "trg_sursa_pub_%s" % t))
            if cur.fetchone()[0] != 1:
                lipsa_pub.append(t)
        detaliu["surse_publice_fara_trigger"] = lipsa_pub
        if lipsa_pub:
            probleme.append({"cod": COD_TRIGGERE_PUBLICE_LIPSA, "ce": lipsa_pub,
                             "diagnostic": "surse din `public` fără trigger: %s"
                                      % ", ".join(lipsa_pub)})

    return {"ok": not probleme, "probleme": probleme, "detaliu": detaliu}


def verifica_triggerele(conn):
    """CE LIPSEȘTE, ca listă. Migrarea trebuie să poată fi VERIFICATĂ, nu doar rulată.

    Aserțiune anti-vacuu inclusă: dacă interogarea n-a găsit **nicio** firmă, se spune — altfel un
    domeniu de căutare greșit ar raporta „0 lipsă" despre o lume pe care n-o vede."""
    asteptate = tabele_cu_trigger()
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE activ ORDER BY id")
        firme = cur.fetchall()
        cur.execute(
            "SELECT n.nspname, c.relname FROM pg_trigger t "
            "  JOIN pg_class c ON c.oid = t.tgrelid "
            "  JOIN pg_namespace n ON n.oid = c.relnamespace "
            " WHERE t.tgname LIKE 'trg_sursa_%%' AND NOT t.tgisinternal")
        au = {(s, r) for s, r in cur.fetchall()}
        cur.execute(
            "SELECT count(*) FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid "
            " WHERE t.tgname = 'trg_tip_firma' AND NOT t.tgisinternal")
        proiectii = cur.fetchone()[0]
    lipsa = []
    for tid, schema in firme:
        for t in asteptate:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass(%s)", ("%s.%s" % (schema, t),))
                if cur.fetchone()[0] is None:
                    continue
            if (schema, t) not in au:
                lipsa.append((schema, t))
    return {"firme_vazute": len(firme), "lipsa": lipsa, "proiectii_tip_firma": proiectii,
            "domeniu_gol": len(firme) == 0}


#: INSTANTANEUL de sănătate al infrastructurii, actualizat de bucla de sănătate a aplicației
#: (`main._verifica_si_alerta`, la 5 minute) și citit de `/admin/sanatate`. NU se calculează în
#: calea de cerere: o verificare per cerere ar întreba catalogul de zeci de ori pe secundă, adică
#: exact felul de muncă pe care P2 a scos-o din cererea interactivă.
_SANATATE = {"ok": None, "verificat_la": None, "probleme": [], "detaliu": {}}


def stare_infrastructura():
    """Ultimul rezultat cunoscut al verificării de drift. `ok=None` = încă neverificat.

    *`None` nu e `False` și nu e `True`:* un serviciu abia pornit n-a apucat să verifice, iar a
    spune „ok" despre ceva ce n-ai măsurat e chiar clasa de defect pe care P2 o repară."""
    return dict(_SANATATE)


def verifica_drift(conn, acum=None):
    """VERIFICARE PERIODICĂ, **strict read-only**: nu creează și nu repară nimic.

    **De ce există, deși pornirea e fail-closed.** `verifica_infrastructura` apără momentul
    pornirii. Dacă după aceea cineva rulează `DROP TRIGGER` — o migrare externă, o mână pe `psql`
    —, aplicația ar afla abia la următoarea repornire, iar între timp rezumatele firmei aceleia ar
    rămâne `curent` fără ca nimic să le mai invalideze.

    **Detectează și alertează; NU repară.** O buclă de sănătate care ar recrea singură triggerele
    ar ascunde chiar semnalul: driftul ar dispărea din log, iar cauza (cine le-a șters, și de ce)
    n-ar mai fi căutată de nimeni. Repararea rămâne un act deliberat — o repornire, care trece
    oricum prin migrare."""
    import datetime
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    r = verifica_infrastructura(conn)
    _SANATATE.update({"ok": bool(r["ok"]), "verificat_la": acum,
                      "probleme": r["probleme"], "detaliu": r["detaliu"]})
    if not r["ok"]:
        for p in r["probleme"]:
            _log().critical("[P2] DRIFT DE INFRASTRUCTURĂ [%s] la %s: %s | %s",
                            p["cod"], acum.isoformat(), p["diagnostic"], p["ce"])
    return dict(_SANATATE)


# ============================================================================
#  SCRIEREA
# ============================================================================
def scrie(conn, tenant_id, aspect, date, versiune, epoca="", stare_calcul=CALCUL_OK,
          incercari=0, urmatoarea_incercare=None):
    with conn.cursor() as cur:
        cur.execute(
            # upsert-ok: rezumatul e o valoare DERIVATĂ, recalculabilă din sursă. A o suprascrie cu
            # una mai nouă e chiar scopul; nu e o intrare de utilizator care s-ar pierde.
            "INSERT INTO public.firma_rezumat (tenant_id, aspect, date, versiune_sursa, "
            "        calculat_la, epoca, stare_calcul, incercari, urmatoarea_incercare) "
            "VALUES (%s, %s, %s::jsonb, %s, now(), %s, %s, %s, %s) "
            "ON CONFLICT (tenant_id, aspect) DO UPDATE "
            "SET date = EXCLUDED.date, versiune_sursa = EXCLUDED.versiune_sursa, "
            "    calculat_la = EXCLUDED.calculat_la, epoca = EXCLUDED.epoca, "
            "    stare_calcul = EXCLUDED.stare_calcul, incercari = EXCLUDED.incercari, "
            "    urmatoarea_incercare = EXCLUDED.urmatoarea_incercare",
            (tenant_id, aspect, json.dumps(date, ensure_ascii=False, default=str), versiune,
             epoca, stare_calcul, incercari, urmatoarea_incercare))


def versiune_aspect(conn, tenant_id, aspect):
    """Versiunea CURENTĂ a unui aspect = suma contoarelor tabelelor lui. Se citește ÎNAINTE de
    calcul — altfel un calcul lung ar ștampila o versiune apărută în timpul lui."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COALESCE(sum(s.versiune), 0) FROM public.firma_sursa_versiune s "
            "  JOIN public.firma_aspect_sursa m ON m.tabela = s.tabela "
            " WHERE s.tenant_id = %s AND m.aspect = %s", (tenant_id, aspect))
        return cur.fetchone()[0]


def versiuni_aspecte(conn, tenant_id, aspecte):
    """Versiunile mai multor aspecte ale unei firme, într-o interogare."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT m.aspect, COALESCE(sum(s.versiune), 0) "
            "  FROM unnest(%s::text[]) AS m0(aspect) "
            "  JOIN public.firma_aspect_sursa m ON m.aspect = m0.aspect "
            "  LEFT JOIN public.firma_sursa_versiune s "
            "         ON s.tabela = m.tabela AND s.tenant_id = %s "
            " GROUP BY m.aspect", (list(aspecte), tenant_id))
        gasite = dict(cur.fetchall())
    return {a: gasite.get(a, 0) for a in aspecte}


# ============================================================================
#  CITIREA — o singură interogare pentru tot portofoliul
# ============================================================================
def citeste(conn, tenant_ids, aspecte=None, azi=None):
    """**O SINGURĂ interogare pentru tot portofoliul și toate aspectele cerute.**

    `{tenant_id: {aspect: {date, stare, calculat_la, versiune_sursa, versiune_curenta, epoca}}}`.

    `stare` se DERIVĂ, niciodată nu se citește dintr-o coloană de stare:
      * fără rând                      -> `lipseste`
      * ultimul calcul a ridicat       -> `eroare`
      * versiunea surselor s-a schimbat-> `invalidat`
      * **epoca s-a schimbat**         -> `invalidat`  (ziua de ieri nu mai descrie ziua de azi)
      * altfel                         -> `curent`

    Epoca se calculează în Python și intră ca al doilea vector în `unnest`, alături de aspecte:
    astfel ceasul e citit O DATĂ, de apelant, nu de fiecare rând — două rânduri ale aceleiași
    cereri nu pot cădea de o parte și de alta a miezului nopții."""
    from core.common import azi_ro as _azi_ro
    aspecte = list(aspecte or TOATE)
    if not tenant_ids:
        return {}
    azi = azi or _azi_ro()
    epoci = [epoca_pentru(a, azi) for a in aspecte]

    with conn.cursor() as cur:
        cur.execute(
            "WITH v AS ("
            "  SELECT s.tenant_id, m.aspect, sum(s.versiune)::bigint AS versiune "
            "    FROM public.firma_sursa_versiune s "
            "    JOIN public.firma_aspect_sursa m ON m.tabela = s.tabela "
            "   WHERE s.tenant_id = ANY(%s) AND m.aspect = ANY(%s) "
            "   GROUP BY 1, 2) "
            "SELECT t.id, a.aspect, r.date, r.versiune_sursa, r.calculat_la, "
            "       COALESCE(v.versiune, 0), r.epoca, a.epoca_acum, r.stare_calcul, r.incercari "
            "  FROM unnest(%s::int[]) AS t(id) "
            " CROSS JOIN unnest(%s::text[], %s::text[]) AS a(aspect, epoca_acum) "
            "  LEFT JOIN public.firma_rezumat r "
            "         ON r.tenant_id = t.id AND r.aspect = a.aspect "
            "  LEFT JOIN v ON v.tenant_id = t.id AND v.aspect = a.aspect",
            (list(tenant_ids), aspecte, list(tenant_ids), aspecte, epoci))
        randuri = cur.fetchall()

    out = {}
    for (tid, aspect, date, v_calc, calculat_la, v_acum, epoca, epoca_acum,
         stare_calcul, incercari) in randuri:
        d = out.setdefault(tid, {})
        if date is None:
            d[aspect] = {"date": None, "stare": LIPSESTE, "calculat_la": None,
                         "versiune_sursa": None, "versiune_curenta": v_acum,
                         "epoca": None, "epoca_acum": epoca_acum, "incercari": 0}
            continue
        if stare_calcul == CALCUL_EROARE:
            stare = EROARE
        elif v_calc != v_acum or (epoca or "") != (epoca_acum or ""):
            stare = INVALIDAT
        else:
            stare = CURENT
        d[aspect] = {"date": date, "calculat_la": calculat_la, "stare": stare,
                     "versiune_sursa": v_calc, "versiune_curenta": v_acum,
                     "epoca": epoca, "epoca_acum": epoca_acum,
                     "incercari": incercari or 0}
    return out


# ============================================================================
#  RECALCULAREA
# ============================================================================
#: Acordajul lucrătorului stă în `core/cron.py`, lângă `RITMURI` — vezi motivul scris acolo.
BACKOFF_MIN = _cron.BACKOFF_FIRMA_REZUMAT_MIN


def _urmatoarea_incercare(incercari):
    import datetime
    idx = min(max(incercari - 1, 0), len(BACKOFF_MIN) - 1)
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=BACKOFF_MIN[idx])


def _incercari_curente(conn, tenant_id, aspect):
    with conn.cursor() as cur:
        cur.execute("SELECT incercari FROM public.firma_rezumat "
                    " WHERE tenant_id = %s AND aspect = %s", (tenant_id, aspect))
        r = cur.fetchone()
    return (r[0] or 0) if r else 0


def recalculeaza_firma(tenant_id, schema, aspecte=None, deschide=None, azi=None):
    """Recalculează aspectele UȘOARE ale unei firme, într-o singură conexiune la schema ei.

    Versiunea se citește ÎNAINTE de calcul — altfel un calcul lung ar ștampila o versiune apărută
    în timpul lui, iar rezultatul ar părea curent fără să fie. Eroarea de calcul NU devine un
    rezultat curent: se scrie cu `stare_calcul = 'eroare'`, deci citirea o dă `eroare`."""
    from core import db as _db
    from core.common import azi_ro as _azi_ro
    deschide = deschide or _db.get_conn
    azi = azi or _azi_ro()
    aspecte = [a for a in (aspecte or ASPECTE_USOARE) if a in ASPECTE_USOARE]

    with _db.get_conn() as c:
        v = versiuni_aspecte(c, tenant_id, aspecte)
        incercari = {a: _incercari_curente(c, tenant_id, a) for a in aspecte}

    valori, erori = {}, {}
    with deschide(schema) as cs:
        for a in aspecte:
            try:
                valori[a] = ASPECTE[a]["calcul"](cs, schema)
            except Exception as e:      # noqa: BLE001 — eroarea devine STARE declarată, nu valoare
                erori[a] = "%s: %s" % (type(e).__name__, e)

    with _db.get_conn() as c:
        for a, date in valori.items():
            scrie(c, tenant_id, a, date, v[a], epoca=epoca_pentru(a, azi),
                  stare_calcul=CALCUL_OK, incercari=0, urmatoarea_incercare=None)
        for a, mesaj in erori.items():
            n = incercari[a] + 1
            scrie(c, tenant_id, a, {"eroare": mesaj}, v[a], epoca=epoca_pentru(a, azi),
                  stare_calcul=CALCUL_EROARE, incercari=n,
                  urmatoarea_incercare=_urmatoarea_incercare(n))
        c.commit()
    return {"valori": valori, "erori": erori}


def recalculeaza_greu(tenant_id, schema, azi=None, ctx=None, nume=None, cui=None):
    """Recalculează `termene` și `control_fiscal` pentru o firmă.

    Chemată de lucrător / la invalidare, **niciodată dintr-o cerere interactivă**. Măsurat înainte
    de P2, la 1000 de firme, într-o singură cerere: `control-fiscal` — 278.882 de interogări, 12.001
    de conexiuni, **70,8 s**; `termene` — 8.000 de interogări, 3.001 de conexiuni, **12,9 s**.

    Calculul e CHEMAT EXACT CA ÎNAINTE (`control_fiscal_api.evalueaza_firma`,
    `main._construieste_contabil`, `main._termene_una_firma`), ca să nu existe două definiții ale
    aceleiași cifre."""
    from core import db as _db
    from core.common import azi_ro as _azi_ro
    azi = azi or _azi_ro()

    with _db.get_conn() as c:
        v = versiuni_aspecte(c, tenant_id, list(ASPECTE_GRELE))
        incercari = {a: _incercari_curente(c, tenant_id, a) for a in ASPECTE_GRELE}
        if nume is None:
            with c.cursor() as cur:
                cur.execute("SELECT nume, cui FROM public.tenants WHERE id = %s", (tenant_id,))
                r = cur.fetchone()
            nume, cui = (r[0], r[1]) if r else (None, None)
        # CTX CU ACCES LA FIRMA. Doua sub-verificari din `_construieste_contabil` (stocuri, praguri
        # Intrastat) trec prin `_schema_sau_404(ctx, tenant_id)`; fara un utilizator care are acces,
        # ele cad pe „gri" cu 404 — adica verdictul firmei ar depinde de cine il cere. Se alege
        # administratorul cabinetului EI.
        if not (ctx or {}).get("uid"):
            with c.cursor() as cur:
                cur.execute(
                    "SELECT u.id FROM public.users u "
                    "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                    " WHERE t.id = %s AND u.rol = 'admin_firma' AND u.activ "
                    " ORDER BY u.id LIMIT 1", (tenant_id,))
                r = cur.fetchone()
            ctx = {"uid": r[0]} if r else {"uid": None}

    valori, erori = {}, {}

    # ── control_fiscal ─────────────────────────────────────────────────────
    try:
        import main as _main
        from core import control_fiscal_api as _cf
        with _db.get_conn(schema) as cs, _db.get_conn() as cp:
            r = _cf.evalueaza_firma(cs, cp, tenant_id, schema, azi)
        contabil, _vc = _main._construieste_contabil(schema, tenant_id, ctx, azi.year, azi.month,
                                                     r.get("regim_tva_anaf"))
        valori["control_fiscal"] = {
            "stare": _main.pastila_firma(r["stare"], contabil),
            "lipsa": len(r.get("lipsa") or []), "urmarit": len(r.get("urmarit") or []),
            "neclar": len(r.get("neclar") or []), "contabil": contabil}
    except Exception as e:      # noqa: BLE001 — eroarea devine STARE declarată, nu tăcere
        erori["control_fiscal"] = "%s: %s" % (type(e).__name__, e)

    # ── termene — prin blocul EXTRAS din rută; el își deschide singur conexiunile ──
    try:
        import main as _main2
        ev, neev = _main2._termene_una_firma({"id": tenant_id, "nume": nume, "cui": cui}, ctx, azi)
        valori["termene"] = {"eval": ev, "neevaluat": neev}
    except Exception as e:      # noqa: BLE001
        erori["termene"] = "%s: %s" % (type(e).__name__, e)

    with _db.get_conn() as c:
        for a, date in valori.items():
            scrie(c, tenant_id, a, date, v[a], epoca=epoca_pentru(a, azi),
                  stare_calcul=CALCUL_OK, incercari=0, urmatoarea_incercare=None)
        for a, mesaj in erori.items():
            n = incercari[a] + 1
            scrie(c, tenant_id, a, {"eroare": mesaj}, v[a], epoca=epoca_pentru(a, azi),
                  stare_calcul=CALCUL_EROARE, incercari=n,
                  urmatoarea_incercare=_urmatoarea_incercare(n))
        c.commit()
    return {"valori": valori, "erori": erori}


# ============================================================================
#  LUCRĂTORUL
# ============================================================================
#: Mărimea LOTULUI — `core/cron.py`, lângă `RITMURI`.
LOT_RECALCULARE = _cron.LOT_FIRMA_REZUMAT

#: Cheia spațiului de blocaje consultative. `pg_try_advisory_lock(cheie, tenant_id)` — un întreg
#: fix ales o dată; orice altă valoare ar merge, atâta timp cât e a NOASTRĂ și numai a noastră.
CHEIE_BLOCAJ = 0x1C0A7A

_LOG = None


def _log():
    global _LOG
    if _LOG is None:
        import logging
        _LOG = logging.getLogger("iconta.firma_rezumat")
    return _LOG


def ia_blocajul(conn, tenant_id):
    """`(luat, backend_pid)`. Blocaj de SESIUNE, luat pe conexiunea primită.

    **DE CE SE ÎNTOARCE ȘI PID-UL BACKENDULUI.** `pg_try_advisory_lock` e un blocaj de **sesiune**:
    îl ține conexiunea, nu tranzacția. Prima formă îl lua într-un `with get_conn()` și îl elibera
    în **alt** `with get_conn()` — două împrumuturi din pool, deci fără nicio garanție că e aceeași
    sesiune PostgreSQL. Când nu e, `pg_advisory_unlock` întoarce `false` pe o sesiune care nu ține
    nimic, iar blocajul rămâne agățat de prima conexiune, **la nesfârșit**, până când pool-ul o
    reciclează. *Un blocaj scurs nu se vede ca eroare: se vede ca o firmă care nu se mai
    recalculează niciodată.*

    PID-ul se citește ODATĂ CU luarea blocajului, în aceeași instrucțiune, și se compară la
    eliberare. Așa proba nu e „am folosit aceeași variabilă", ci „a fost același backend"."""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_try_advisory_lock(%s, %s), pg_backend_pid()", (CHEIE_BLOCAJ, tenant_id))
        luat, pid = cur.fetchone()
    return bool(luat), pid


def lasa_blocajul(conn, tenant_id, pid_asteptat=None):
    """`True` dacă blocajul chiar a fost eliberat. **Rezultatul NU se înghite.**

    `pg_advisory_unlock` întoarce `false` când sesiunea curentă nu ține blocajul — adică exact
    simptomul defectului de mai sus. Se logează ca EROARE, cu tot ce trebuie ca să se poată
    diagnostica: firma, backendul care a luat, backendul care eliberează."""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_unlock(%s, %s), pg_backend_pid()", (CHEIE_BLOCAJ, tenant_id))
        eliberat, pid = cur.fetchone()
    if pid_asteptat is not None and pid != pid_asteptat:
        _log().error("[P2] blocajul firmei %s a fost luat pe backendul %s și eliberat pe %s — "
                     "sesiuni DIFERITE, blocajul rămâne agățat de prima",
                     tenant_id, pid_asteptat, pid)
    if not eliberat:
        _log().error("[P2] pg_advisory_unlock(%s, %s) a întors FALSE pe backendul %s: sesiunea nu "
                     "ținea blocajul. Firma poate rămâne blocată pentru turele următoare.",
                     CHEIE_BLOCAJ, tenant_id, pid)
    return bool(eliberat)


def de_recalculat(conn, limita=LOT_RECALCULARE, azi=None, acum=None):
    """PERECHILE (firmă, aspect) care nu mai sunt curente. **Per aspect, nu per firmă.**

    **Ce repară.** Prima formă făcea `LEFT JOIN … WHERE r.tenant_id IS NULL OR r.versiune_sursa <>
    s.versiune`, cu join-ul pe `tenant_id` singur. O firmă care avea rânduri pentru 3 aspecte din 6
    producea 3 rânduri, toate cu versiunea potrivită — deci firma NU ieșea, iar cele 3 aspecte
    lipsă rămâneau `lipseste` **pentru totdeauna**. Se vedea pe ecran ca gri permanent, fără nicio
    eroare nicăieri. Acum se pleacă de la produsul (firme × aspecte), deci un aspect lipsă e la fel
    de vizibil ca unul învechit.

    Firmele sunt luate din `public.tenants` — sursa de adevăr despre ce firme există — nu din tabela
    de contoare: o firmă în care nu s-a scris niciodată n-are rând de contor, și tocmai ea e cea
    care n-a fost calculată deloc.

    Ordinea: erorile care și-au așteptat pasul de reîncercare intră ULTIMELE, ca o firmă care crapă
    în buclă să nu țină locul uneia care doar așteaptă."""
    from core.common import azi_ro as _azi_ro
    import datetime
    azi = azi or _azi_ro()
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    aspecte = list(TOATE)
    epoci = [epoca_pentru(a, azi) for a in aspecte]
    with conn.cursor() as cur:
        cur.execute(
            "WITH v AS ("
            "  SELECT s.tenant_id, m.aspect, sum(s.versiune)::bigint AS versiune "
            "    FROM public.firma_sursa_versiune s "
            "    JOIN public.firma_aspect_sursa m ON m.tabela = s.tabela "
            "   GROUP BY 1, 2) "
            "SELECT t.id, a.aspect, "
            "       (r.tenant_id IS NOT NULL AND r.stare_calcul = %s) AS e_eroare "
            "  FROM public.tenants t "
            " CROSS JOIN unnest(%s::text[], %s::text[]) AS a(aspect, epoca_acum) "
            "  LEFT JOIN public.firma_rezumat r "
            "         ON r.tenant_id = t.id AND r.aspect = a.aspect "
            "  LEFT JOIN v ON v.tenant_id = t.id AND v.aspect = a.aspect "
            " WHERE t.activ "
            "   AND (r.tenant_id IS NULL "
            "        OR r.versiune_sursa <> COALESCE(v.versiune, 0) "
            "        OR COALESCE(r.epoca, '') <> a.epoca_acum "
            "        OR (r.stare_calcul = %s "
            "            AND (r.urmatoarea_incercare IS NULL OR r.urmatoarea_incercare <= %s))) "
            " ORDER BY e_eroare ASC, t.id ASC, a.aspect ASC "
            " LIMIT %s",
            (CALCUL_EROARE, aspecte, epoci, CALCUL_EROARE, acum, limita))
        return [(tid, aspect) for tid, aspect, _e in cur.fetchall()]


def masura_backlog(conn, azi=None, acum=None):
    """CÂT de în urmă e modelul, într-o singură interogare. Pentru SLA, nu pentru decizii.

    **De ce nu ajunge numărul de perechi.** „1000 în așteptare" nu spune dacă ecranele mint de
    zece secunde sau de patru ore. Cifra care contează e **de cât timp așteaptă cea mai veche
    invalidare**.

    **Cum se măsoară, și de ce e un PLAFON SUPERIOR.** Nu ținem istoricul schimbărilor de sursă,
    deci nu știm clipa exactă în care o pereche a devenit învechită; știm doar `calculat_la` —
    când a fost ultima dată bună. Perechea a devenit învechită *după* acel moment, deci
    `acum - calculat_la` e **cel mult** cât așteaptă. Eroarea merge în direcția „pare mai vechi
    decât e", adică o alarmă mai devreme, niciodată una mai târzie. *Se scrie aici ca să nu se
    citească drept măsurătoare exactă.*

    Perechile care n-au fost calculate NICIODATĂ n-au `calculat_la`, deci n-au vârstă — se numără
    separat (`fara_calcul`), nu se topesc într-o medie."""
    from core.common import azi_ro as _azi_ro
    import datetime
    azi = azi or _azi_ro()
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    aspecte = list(TOATE)
    epoci = [epoca_pentru(a, azi) for a in aspecte]
    with conn.cursor() as cur:
        cur.execute(
            "WITH v AS ("
            "  SELECT s.tenant_id, m.aspect, sum(s.versiune)::bigint AS versiune "
            "    FROM public.firma_sursa_versiune s "
            "    JOIN public.firma_aspect_sursa m ON m.tabela = s.tabela "
            "   GROUP BY 1, 2), "
            "restante AS ("
            "  SELECT t.id AS tenant_id, a.aspect, r.tenant_id IS NULL AS fara_calcul, "
            "         r.calculat_la, r.stare_calcul "
            "    FROM public.tenants t "
            "   CROSS JOIN unnest(%s::text[], %s::text[]) AS a(aspect, epoca_acum) "
            "    LEFT JOIN public.firma_rezumat r "
            "           ON r.tenant_id = t.id AND r.aspect = a.aspect "
            "    LEFT JOIN v ON v.tenant_id = t.id AND v.aspect = a.aspect "
            "   WHERE t.activ "
            "     AND (r.tenant_id IS NULL "
            "          OR r.versiune_sursa <> COALESCE(v.versiune, 0) "
            "          OR COALESCE(r.epoca, '') <> a.epoca_acum "
            "          OR r.stare_calcul = %s)) "
            "SELECT count(*), count(DISTINCT tenant_id), "
            "       count(*) FILTER (WHERE fara_calcul), "
            "       count(*) FILTER (WHERE stare_calcul = %s), "
            "       min(calculat_la) "
            "  FROM restante",
            (aspecte, epoci, CALCUL_EROARE, CALCUL_EROARE))
        perechi, firme, fara_calcul, in_eroare, cea_mai_veche = cur.fetchone()
    varsta = None
    if cea_mai_veche is not None:
        varsta = max(0, int((acum - cea_mai_veche).total_seconds()))
    return {"perechi_restante": perechi, "firme_restante": firme,
            "fara_calcul": fara_calcul, "in_eroare": in_eroare,
            "cea_mai_veche_calculat_la": cea_mai_veche,
            "vechime_maxima_sec": varsta}


def recalculeaza_lot(limita=LOT_RECALCULARE, azi=None, ctx=None, opreste=None):
    """Lucrătorul: ia perechile (firmă, aspect) învechite și le recalculează.

    **BLOCAJ, ca două ture să nu lucreze aceeași firmă.** Turele pornesc la 5 minute; o firmă mare
    poate depăși intervalul, iar a doua tură ar recalcula-o în paralel — două calcule scumpe pentru
    același rezultat, și o cursă la scriere. `pg_try_advisory_lock` e **neblocant**: dacă altcineva
    ține firma, tura o sare și trece la următoarea. Blocajul e per FIRMĂ, nu per aspect, fiindcă
    aspectele grele partajează aceeași trecere de calcul.

    **OPRIRE CURATĂ.** `opreste()` e întrebat între firme; la `True`, tura se încheie și RAPORTEAZĂ
    cât a apucat. Nu se abandonează o firmă la jumătate: o firmă începută se termină. Ce n-a apucat
    rămâne invalidat, deci tura următoare îl ia — starea din bază e singurul jurnal de care are
    nevoie, și de-aia nu există unul separat.

    **BACKLOG MARE.** Lotul mărginește o tură, nu munca totală: la 1000 de firme × 5 aspecte, o
    tură ia primele 200 de perechi și restul rămân pentru turele următoare, în ordinea din
    `de_recalculat`. Raportul spune `ramase`, ca un backlog care nu scade să fie vizibil."""
    import time as _time
    from core import db as _db
    from core.common import azi_ro as _azi_ro
    azi = azi or _azi_ro()
    _t0 = _time.time()

    with _db.get_conn() as c:
        perechi = de_recalculat(c, limita, azi=azi)
        ids = sorted({t for t, _a in perechi})
        with c.cursor() as cur:
            cur.execute("SELECT id, schema_name, nume, cui FROM public.tenants "
                        "WHERE id = ANY(%s)", (ids,))
            info = {r[0]: r[1:] for r in cur.fetchall()}

    pe_firma = {}
    for tid, aspect in perechi:
        pe_firma.setdefault(tid, []).append(aspect)

    r = {"perechi": len(perechi), "firme": len(pe_firma), "recalculate": 0, "erori": 0,
         "sarite_blocate": 0, "blocaje_neeliberate": 0, "fara_firma": [], "oprit": False}

    for tid, aspecte in pe_firma.items():
        if opreste and opreste():
            r["oprit"] = True
            break
        d = info.get(tid)
        if not d:
            r["fara_firma"].append(tid)     # contor fără firmă (probă, firmă ștearsă) — se raportează
            continue
        schema, nume, cui = d
        # ┌────────────────────────────────────────────────────────────────────────┐
        # │ IMPORTANT — NU „OPTIMIZA" BLOCUL ĂSTA.                                 │
        # │ `pg_advisory_lock` e la nivel de SESIUNE, nu de tranzacție. `lock_conn` │
        # │ TREBUIE ținută împrumutată din pool până DUPĂ `pg_advisory_unlock`.     │
        # │                                                                        │
        # │ Forma tentantă și GREȘITĂ, care a existat aici și a fost reparată la    │
        # │ auditul din 08.09.2026:                                                │
        # │     iei lock -> întorci conexiunea în pool -> calculezi ->              │
        # │     iei ALTĂ conexiune -> unlock                                        │
        # │ Atunci `pg_advisory_unlock` întoarce `false` pe o sesiune care nu ține  │
        # │ nimic, iar blocajul rămâne agățat de prima conexiune până la reciclare. │
        # │ Nu se vede ca eroare: se vede ca o firmă care nu se mai recalculează.   │
        # │ Gardat de `core/test_p2_infrastructura.py` — a se păstra permanent.     │
        # └────────────────────────────────────────────────────────────────────────┘
        # ── BLOCAJUL SE IA ȘI SE ELIBEREAZĂ PE ACEEAȘI CONEXIUNE ──────────────────
        # `lock_conn` rămâne împrumutată din pool pe TOATĂ durata recalculării firmei. Costă un loc
        # în pool (recalcularea grea mai deschide două), dar e singura formă în care un blocaj de
        # sesiune înseamnă ceva. Vezi `ia_blocajul` pentru ce se întâmpla înainte.
        with _db.get_conn() as lock_conn:
            luat, pid_lock = ia_blocajul(lock_conn, tid)
            if not luat:
                r["sarite_blocate"] += 1
                continue
            try:
                usoare = [a for a in aspecte if a in ASPECTE_USOARE]
                if usoare:
                    x = recalculeaza_firma(tid, schema, aspecte=usoare, azi=azi)
                    r["erori"] += len(x["erori"])
                    r["recalculate"] += len(x["valori"])
                if [a for a in aspecte if a in ASPECTE_GRELE]:
                    # cele două grele se produc printr-o singură trecere; se cer amândouă chiar dacă
                    # doar unul e învechit — a doua oară ar costa la fel de mult
                    x = recalculeaza_greu(tid, schema, azi=azi, ctx=ctx, nume=nume, cui=cui)
                    r["erori"] += len(x["erori"])
                    r["recalculate"] += len(x["valori"])
            finally:
                # `finally`, deci și când recalcularea ridică, și când tura e abandonată. Un blocaj
                # nelăsat ar face firma să pară „în lucru" pentru totdeauna.
                if not lasa_blocajul(lock_conn, tid, pid_lock):
                    r["blocaje_neeliberate"] += 1

    with _db.get_conn() as c:
        b = masura_backlog(c, azi=azi)
    r["ramase"] = b["perechi_restante"]
    r["firme_ramase"] = b["firme_restante"]
    r["fara_calcul"] = b["fara_calcul"]
    r["in_eroare"] = b["in_eroare"]
    r["vechime_maxima_sec"] = b["vechime_maxima_sec"]
    r["secunde"] = round(_time.time() - _t0, 3)
    return r


# ============================================================================
#  PUNCT DE INTRARE — `python3 -m core.firma_rezumat`, din cron, la 5 minute
# ============================================================================
def main():
    """Recalculează perechile învechite. Bate deadman-ul, ca orice job de fundal.

    **De ce la 5 minute și nu o dată pe zi:** rezumatul e ce vede contabilul pe ecranul de portofoliu.
    O firmă atinsă la 9:05 n-are de ce să apară gri până a doua zi.

    **OPRIREA.** `SIGTERM`/`SIGINT` nu omoară tura la mijlocul unei firme: pun un steag pe care
    bucla îl citește între firme. O firmă lăsată necalculată rămâne invalidată, deci tura următoare
    o ia — *singura stare de care are nevoie lucrătorul e cea din bază*."""
    import signal
    from core import cron as _cron, db as _db
    _db.init_pool()

    stop = {"cerut": False}

    def _cere_oprirea(semnal, cadru):
        stop["cerut"] = True
        print("oprire cerută (semnal %s) — termin firma curentă și ies" % semnal, flush=True)

    for s in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(s, _cere_oprirea)
        except (ValueError, OSError):
            pass                            # fără fir principal (test) — nu e motiv de eșec

    r = recalculeaza_lot(opreste=lambda: stop["cerut"])
    try:
        _cron.bate("firma_rezumat")
    except Exception as e:      # noqa: BLE001 — bătaia lipsă nu are voie să pice recalcularea
        print("avertisment: bataia deadman a esuat: %s" % e)
    # Linia de METRICI, cu numele cerute de audit. E o REDARE a raportului de mai sus, nu o a
    # doua sursă: fiecare cifră vine din aceeași cheie a dicționarului. `p2_oldest_pending_age_
    # seconds` e un PLAFON SUPERIOR — vezi `masura_backlog`.
    print("p2_worker_selected=%(perechi)d p2_worker_processed=%(recalculate)d "
          "p2_worker_remaining=%(ramase)d p2_worker_errors=%(erori)d "
          "p2_worker_locked_skips=%(sarite_blocate)d "
          "p2_worker_unlock_failures=%(blocaje_neeliberate)d "
          "p2_worker_duration_seconds=%(secunde)s "
          "p2_oldest_pending_age_seconds=%(vechime_maxima_sec)s "
          "p2_worker_firms=%(firme)d p2_pending_never_computed=%(fara_calcul)d "
          "p2_pending_in_error=%(in_eroare)d p2_worker_stopped=%(oprit)s "
          "p2_worker_orphan_counters=%(fara_firma)s" % r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
